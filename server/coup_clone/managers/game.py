import random
import string
from collections import Counter
from dataclasses import dataclass
from sqlite3 import IntegrityError
from typing import Optional, Tuple

from socketio import AsyncServer

from coup_clone.actions import get_action
from coup_clone.db.events import EventsTable
from coup_clone.db.games import GamesTable, GameState, TurnAction, TurnState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable, PlayerState
from coup_clone.managers.exceptions import (
    GameFullException,
    GameNotFoundException,
    InvalidGameStateException,
    NotEnoughPlayersException,
    NotPlayerTurnException,
    PlayerAlreadyInGameException,
    PlayerNotHostException,
    PlayerNotInGameException,
)
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.models import Game, Player, get_shuffled_deck
from coup_clone.request import Request


@dataclass
class ExchangeInfluence:
    influence: Influence
    selected: bool


class GameManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        notifications_manager: NotificationsManager,
    ):
        self.socket_server = socket_server
        self.notifications_manager = notifications_manager

    async def _add_log_message(self, game: Game, message: str) -> None:
        async with game.conn.cursor() as cursor:
            await EventsTable.create(
                cursor,
                game_id=game.id,
                message=message,
            )
    
    async def _get_player_in_game(self, request: Request) -> Player:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()
        return player

    async def create(self, request: Request) -> None:
        current_player = await request.session.get_player()
        if current_player is not None:
            raise PlayerAlreadyInGameException(current_player.game_id)

        game_id = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
        game = await Game.create(request.conn, id=game_id, deck="".join(str(c) for c in get_shuffled_deck()))
        hand = await game.take_from_deck()
        player = await Player.create(request.conn, game_id=game.id, host=True, influence_a=hand[0], influence_b=hand[1])
        await request.session.set_player(player.id)
        await game.reset_turn_state(player.id)
        await request.conn.commit()
        self.socket_server.enter_room(request.sid, game.id)
        await self.notifications_manager.notify_session(request.session)

    async def join(self, request: Request, game_id: str) -> Tuple[str, PlayerRow]:
        async with request.conn.cursor() as cursor:
            current_player = await request.session.get_player()
            if current_player is not None:
                raise PlayerAlreadyInGameException(current_player.game_id)
            game_row = await GamesTable.get(cursor, game_id)
            if game_row is None:
                raise GameNotFoundException(game_id)
            game = Game(request.conn, await GamesTable.get(cursor, game_id))
            hand = await game.take_from_deck()
            try:
                player = await PlayersTable.create(cursor, game_id=game_id, influence_a=hand[0], influence_b=hand[1])
            except IntegrityError as e:
                if str(e) == "Game full":
                    raise GameFullException(game_id)
            await request.session.set_player(player.id)
            await request.conn.commit()

        self.socket_server.enter_room(request.sid, game_id)
        await self.notifications_manager.broadcast_game(request.conn, game_id)
        await self.notifications_manager.notify_session(request.session)
        return (game_id, player)

    async def leave(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise Exception("Session is already not in a game")

        game = await player.get_game()

        if game.row.player_turn_id == player.id:
            next_player = await game.get_next_player_turn()
            if next_player is None or next_player.id == player.id:
                await game.update(player_turn_id=None)
            else:
                await game.next_player_turn()

        if game.row.state == GameState.RUNNING:
            await player.update(
                revealed_influence_a=True,
                revealed_influence_b=True,
            )

            players_remaining = [p for p in await game.get_players() if not p.is_out]
            await self._add_log_message(game, f"{player.row.name} left the game")
            if len(players_remaining) == 1:
                winner = players_remaining[0]
                await self._add_log_message(game, f"{winner.row.name} wins the game!")
                await game.update(state=GameState.FINISHED, winner_id=winner.id)
        elif game.row.state == GameState.LOBBY:
            await game.return_to_deck([player.influence_a, player.influence_b])
            await player.delete()

        await request.session.clear_current_player()
        await request.conn.commit()
        self.socket_server.leave_room(request.sid, game.id)
        await self.notifications_manager.broadcast_game(request.conn, game.id)
        await self.notifications_manager.notify_session(request.session)

    async def set_name(self, request: Request, name: str) -> None:
        async with request.conn.cursor() as cursor:
            player = await self._get_player_in_game(request)
            await PlayersTable.update(cursor, player.id, name=name, state=PlayerState.READY)
            await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def start(self, request: Request) -> None:
        async with request.conn.cursor() as cursor:
            player = await self._get_player_in_game(request)
            game = await player.get_game()
            players = await game.get_players()
            if len(players) < 2:
                raise NotEnoughPlayersException(game.id)
            await GamesTable.update(cursor, player.game_id, state=GameState.RUNNING)
            await game.next_player_turn()
            await self._add_log_message(game, "Welcome to Coup!")
            await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def take_action(self, request: Request, turn_action: TurnAction, target_id: Optional[int]) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()
        if game.row.player_turn_id != player.id:
            raise NotPlayerTurnException()

        if game.row.turn_state != TurnState.START:
            raise InvalidGameStateException(game.id)

        action = get_action(turn_action)

        if action.is_targetted:
            if target_id is None:
                raise Exception("Missing target")
            target = await Player.get(request.conn, target_id)
            if target is None:
                raise Exception("Really missing target")

        if action.cost > 0:
            if action.cost > player.row.coins:
                raise Exception("Player can't affort it")
            await player.decrement_coins(action.cost)

        await game.update(turn_action=turn_action, target_id=target_id)

        if action.influence is None and not action.can_be_blocked_by:
            if action.effect:
                await action.effect(game)
            await self._add_log_message(game, action.success_message.format(
                player=player.row.name,
                target=target.row.name if target is not None else None
            ))
            if action.next_state == TurnState.START:
                await game.next_player_turn()
            else:
                await game.update(turn_state=action.next_state)
        else:
            await game.update(
                turn_state=TurnState.ATTEMPTED,
            )
            await self._add_log_message(game, action.attempt_message.format(
                player=player.row.name,
                target=target.row.name if target is not None else None
            ))

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def accept_action(self, request: Request) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()
        if game.row.turn_state != TurnState.ATTEMPTED:
            raise Exception("Invalid turn state")

        await player.update(accepts_action=True)

        all_players_accepted = await game.all_players_accepted()
        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("Get a better exception..")

        if all_players_accepted:
            action = get_action(game.row.turn_action)
            if action.effect:
                await action.effect(game)
            target = await game.get_target_player()
            await self._add_log_message(game, action.success_message.format(
                player=player.row.name,
                target=target.row.name if target is not None else None
            ))
            if action.next_state == TurnState.START:
                await game.next_player_turn()
            else:
                await game.update(turn_state=action.next_state)

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def reveal_influence(self, request: Request, influence: Influence) -> None:
        # This is all horrible, must refactor... writing this makes me feel better in the meantime
        player = await self._get_player_in_game(request)
        game = await player.get_game()

        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("Current player is missing")

        if game.row.turn_state not in {
            TurnState.REVEALING,
            TurnState.TARGET_REVEALING,
            TurnState.CHALLENGED,
            TurnState.CHALLENGER_REVEALING,
            TurnState.BLOCK_CHALLENGED,
            TurnState.BLOCK_CHALLENGER_REVEALING,
        }:
            raise Exception("Invalid turn state")

        if (
            game.row.turn_state == TurnState.REVEALING or game.row.turn_state == TurnState.CHALLENGED
        ) and player.id != game.row.player_turn_id:
            raise Exception("Expecting current turn player to reveal")

        if game.row.turn_state == TurnState.TARGET_REVEALING and player.id != game.row.target_id:
            raise Exception("Expecting current turn target to reveal")

        if game.row.turn_state == TurnState.CHALLENGER_REVEALING and player.id != game.row.challenged_by_id:
            raise Exception("Expecting current turn challenger to reveal")

        if game.row.turn_state == TurnState.BLOCK_CHALLENGED and player.id != game.row.blocked_by_id:
            raise Exception("Expecting blocker to reveal")

        if game.row.turn_state == TurnState.BLOCK_CHALLENGER_REVEALING and player.id != game.row.block_challenged_by_id:
            raise Exception("Expecting blocker to reveal")

        revealed = None
        if player.row.influence_a == influence and not player.row.revealed_influence_a:
            revealed = "A"
            await player.update(revealed_influence_a=True)
        elif player.row.influence_b == influence and not player.row.revealed_influence_b:
            revealed = "B"
            await player.update(revealed_influence_b=True)
        else:
            raise Exception("Invalid influence for reveal")

        await self._add_log_message(game, f"{player.row.name} revealed a {influence.name}")

        action = get_action(game.row.turn_action)
        target = await game.get_target_player()
        match game.row.turn_state:
            case TurnState.CHALLENGED:
                if action.influence == influence:
                    if action.effect:
                        await action.effect(game)
                    await game.return_to_deck([influence])
                    new_card = await game.take_from_deck(1)
                    await self._add_log_message(game, action.success_message.format(
                        player=player.row.name,
                        target=target.row.name if target is not None else None
                    ))
                    match revealed:
                        case "A":
                            await player.update(influence_a=new_card[0], revealed_influence_a=False)
                        case "B":
                            await player.update(influence_b=new_card[0], revealed_influence_b=False)
                    await game.update(turn_state=TurnState.CHALLENGER_REVEALING)
                else:
                    await game.next_player_turn()

            case TurnState.BLOCK_CHALLENGED:
                if influence in action.can_be_blocked_by:
                    await self._add_log_message(game, f"{player.row.name} succesfully blocked {current_player.row.name}")
                    await game.update(turn_state=TurnState.BLOCK_CHALLENGER_REVEALING)
                else:
                    if action.effect:
                        await action.effect(game)
                    await self._add_log_message(game, action.success_message.format(
                        player=player.row.name,
                        target=target.row.name if target is not None else None
                    ))
                    if action.next_state == TurnState.START:
                        await game.next_player_turn()
                    else:
                        await game.update(turn_state=action.next_state)

            case _:
                await game.update(turn_state=action.next_state)

        if player.is_out:
            await self._add_log_message(game, f"{player.row.name} is out of the game!")

        players_remaining = [p for p in await game.get_players() if not p.is_out]
        if len(players_remaining) == 1:
            winner = players_remaining[0]
            await self._add_log_message(game, f"{winner.row.name} wins the game!")
            await game.update(state=GameState.FINISHED, winner_id=winner.id)

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)
        await self.notifications_manager.notify_player(request.conn, player)

    async def challenge(self, request: Request) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()

        if game.row.turn_state != TurnState.ATTEMPTED:
            raise Exception("Invalid turn state")

        if game.row.player_turn_id == player.id:
            raise Exception("Cannot challenge self")

        action = get_action(game.row.turn_action)
        if action.influence is None:
            raise Exception("Cannot challenge this action")

        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("Get a better exception..")

        await self._add_log_message(game, f"{player.row.name} challenges {current_player.row.name}")
        await game.update(turn_state=TurnState.CHALLENGED, challenged_by_id=player.id)
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def block(self, request: Request) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()
        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("No current player")

        if game.row.turn_state != TurnState.ATTEMPTED:
            raise Exception("Invalid turn state")

        if game.row.player_turn_id == player.id:
            raise Exception("Cannot block self")

        if game.row.target_id is not None and game.row.target_id != player.id:
            raise Exception("Invalid requester for blocking")

        action = get_action(game.row.turn_action)

        if not action.can_be_blocked_by:
            raise Exception("Cannot block current action")

        await game.update(turn_state=TurnState.BLOCKED, blocked_by_id=player.id)
        await self._add_log_message(game, f"{player.row.name} blocks {current_player.row.name}")
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def accept_block(self, request: Request) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()
        if player.id != game.row.player_turn_id:
            raise Exception("Current turn player can only accept blocks")

        await self._add_log_message(game, f"{player.row.name} backs down")
        await game.next_player_turn()
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def challenge_block(self, request: Request) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()
        if player.id == game.row.blocked_by_id:
            raise Exception("Player can't challenge own block")

        blocking = await game.get_blocking_player()
        if blocking is None:
            raise Exception("There's no blockign player")

        await game.update(turn_state=TurnState.BLOCK_CHALLENGED, block_challenged_by_id=player.id)
        await self._add_log_message(game, f"{player.row.name} challenged {blocking.row.name}")
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def exchange(self, request: Request, exchanges: list[ExchangeInfluence]) -> None:
        player = await self._get_player_in_game(request)
        game = await player.get_game()
        expected_influence = [Influence(int(i)) for i in game.row.deck[-2:]]
        if not player.row.revealed_influence_a:
            expected_influence.append(player.influence_a)
        if not player.row.revealed_influence_b:
            expected_influence.append(player.influence_b)
        received_influence = [e.influence for e in exchanges]

        if Counter(expected_influence) != Counter(received_influence):
            raise Exception("Received unexpected influence")

        return_to_deck = [e.influence for e in exchanges if not e.selected]
        keep_in_hand = [e.influence for e in exchanges if e.selected]

        if len(return_to_deck) != 2:
            raise Exception("Must return 2 to deck")

        await game.take_from_deck(n=2)
        await game.return_to_deck(return_to_deck)

        if len(keep_in_hand) == 1:
            if player.row.revealed_influence_a:
                await player.update(influence_b=keep_in_hand[0])
            elif player.row.revealed_influence_b:
                await player.update(influence_a=keep_in_hand[0])
            else:
                raise Exception("Something weird has happened")
        elif len(keep_in_hand) == 2:
            await player.update(
                influence_a=keep_in_hand[0],
                influence_b=keep_in_hand[1],
            )
        else:
            raise Exception("Something weird has happened")

        await self._add_log_message(game, f"{player.row.name} returns 2 cards to the deck")
        await game.next_player_turn()

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)
        await self.notifications_manager.notify_player(request.conn, player)

    async def restart(self, request: Request) -> None:
        player = await self._get_player_in_game(request)
        if not player.row.host:
            raise PlayerNotHostException()

        game = await player.get_game()
        if game.row.state != GameState.FINISHED:
            raise InvalidGameStateException(game.id)

        await game.reset()
        await self._add_log_message(game, f"{player.row.name} has restarted the game")

        await request.conn.commit()

        await self.notifications_manager.broadcast_reset(request)
