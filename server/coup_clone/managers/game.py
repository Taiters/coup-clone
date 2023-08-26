import random
import string
from collections import Counter
from dataclasses import dataclass
from sqlite3 import IntegrityError
from typing import Optional, Tuple

from socketio import AsyncServer

from coup_clone.db.events import EventsTable
from coup_clone.db.games import GamesTable, GameState, TurnAction, TurnState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable, PlayerState
from coup_clone.managers.exceptions import (
    GameFullException,
    GameNotFoundException,
    NotEnoughPlayersException,
    NotPlayerTurnException,
    PlayerAlreadyInGameException,
    PlayerNotInGameException,
)
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.models import Game, Player
from coup_clone.request import Request

DECK = [
    Influence.DUKE,
    Influence.DUKE,
    Influence.DUKE,
    Influence.CAPTAIN,
    Influence.CAPTAIN,
    Influence.CAPTAIN,
    Influence.ASSASSIN,
    Influence.ASSASSIN,
    Influence.ASSASSIN,
    Influence.CONTESSA,
    Influence.CONTESSA,
    Influence.CONTESSA,
    Influence.AMBASSADOR,
    Influence.AMBASSADOR,
    Influence.AMBASSADOR,
]


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

    async def _next_player_turn(self, game: Game) -> None:
        next_player = await game.get_next_player_turn()
        if next_player is None:
            raise Exception("No next player available")
        await game.reset_turn_state(next_player.id)

    async def create(self, request: Request) -> None:
        current_player = await request.session.get_player()
        if current_player is not None:
            raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

        game_id = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
        game = await Game.create(
            request.conn, id=game_id, deck="".join(str(c.value) for c in random.sample(DECK, k=len(DECK)))
        )
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
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)
            game_row = await GamesTable.get(cursor, game_id)
            if game_row is None:
                raise GameNotFoundException()
            game = Game(request.conn, await GamesTable.get(cursor, game_id))
            hand = await game.take_from_deck()
            try:
                player = await PlayersTable.create(cursor, game_id=game_id, influence_a=hand[0], influence_b=hand[1])
            except IntegrityError as e:
                if str(e) == "Game full":
                    raise GameFullException()
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
                await self._next_player_turn(game)

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
            player = await request.session.get_player()
            if player is None:
                raise PlayerNotInGameException()
            await PlayersTable.update(cursor, player.id, name=name, state=PlayerState.READY)
            await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def start(self, request: Request) -> None:
        async with request.conn.cursor() as cursor:
            player = await request.session.get_player()
            if player is None:
                raise PlayerNotInGameException()
            game = await player.get_game()
            players = await game.get_players()
            if len(players) < 2:
                raise NotEnoughPlayersException()
            await GamesTable.update(cursor, player.game_id, state=GameState.RUNNING)
            await self._next_player_turn(game)
            await self._add_log_message(game, "Welcome to Coup!")
            await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def take_action(self, request: Request, turn_action: TurnAction, target_id: Optional[int]) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()
        game = await player.get_game()
        if game.row.player_turn_id != player.id:
            raise NotPlayerTurnException()

        match turn_action:
            case TurnAction.INCOME:
                await player.increment_coins()
                await self._next_player_turn(game)
                await self._add_log_message(game, f"{player.row.name} took Income")
            case TurnAction.FOREIGN_AID:
                await game.update(
                    turn_action=TurnAction.FOREIGN_AID,
                    turn_state=TurnState.ATTEMPTED,
                )
                await self._add_log_message(game, f"{player.row.name} attempts to take Foreign Aid")
            case TurnAction.TAX:
                await game.update(
                    turn_action=TurnAction.TAX,
                    turn_state=TurnState.ATTEMPTED,
                )
                await self._add_log_message(game, f"{player.row.name} attempts to take Tax")
            case TurnAction.STEAL:
                if target_id is None:
                    raise Exception("Steal must have a target")
                target = await Player.get(request.conn, target_id)
                if target is None:
                    raise Exception("Find a better exception...")
                await self._add_log_message(game, f"{player.row.name} attempts to steal from {target.row.name}")
                await game.update(
                    turn_action=TurnAction.STEAL,
                    turn_state=TurnState.ATTEMPTED,
                    target_id=target.id,
                )
            case TurnAction.EXCHANGE:
                await game.update(
                    turn_action=TurnAction.EXCHANGE,
                    turn_state=TurnState.ATTEMPTED,
                )
                await self._add_log_message(game, f"{player.row.name} attempts to Exchange")
            case TurnAction.ASSASSINATE:
                if target_id is None:
                    raise Exception("Assasinate must have a target")
                target = await Player.get(request.conn, target_id)
                if target is None:
                    raise Exception("Find a better exception...")
                await self._add_log_message(game, f"{player.row.name} attempts to assasinate {target.row.name}")
                await player.decrement_coins(amount=3)
                await game.update(
                    turn_action=TurnAction.ASSASSINATE,
                    turn_state=TurnState.ATTEMPTED,
                    target_id=target.id,
                )
            case TurnAction.COUP:
                if target_id is None:
                    raise Exception("Coup must have a target")
                target = await Player.get(request.conn, target_id)
                if target is None:
                    raise Exception("Find a better exception...")
                await self._add_log_message(game, f"{player.row.name} started a coup on {target.row.name}")
                await player.decrement_coins(amount=7)
                await game.update(
                    turn_action=TurnAction.COUP,
                    turn_state=TurnState.TARGET_REVEALING,
                    target_id=target.id,
                )
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def accept_action(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

        game = await player.get_game()
        if game.row.turn_state != TurnState.ATTEMPTED:
            raise Exception("Invalid turn state")

        await player.update(accepts_action=True)

        all_players_accepted = await game.all_players_accepted()
        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("Get a better exception..")

        if all_players_accepted:
            match game.row.turn_action:
                case TurnAction.FOREIGN_AID:
                    await self._add_log_message(game, f"{current_player.row.name} succesfully took Foreign Aid")
                    await current_player.increment_coins(amount=2)
                    await self._next_player_turn(game)
                case TurnAction.TAX:
                    await self._add_log_message(game, f"{current_player.row.name} succesfully took Tax")
                    await current_player.increment_coins(amount=3)
                    await self._next_player_turn(game)
                case TurnAction.STEAL:
                    target = await game.get_target_player()
                    if target is None:
                        raise Exception("Find a better exception...")
                    await self._add_log_message(
                        game, f"{current_player.row.name} succesfully stole from {target.row.name}"
                    )
                    await current_player.increment_coins(amount=2)
                    await target.decrement_coins(amount=2)
                    await self._next_player_turn(game)
                case TurnAction.EXCHANGE:
                    await self._add_log_message(game, f"{current_player.row.name} draws 2 cards to exchange")
                    await game.update(turn_state=TurnState.EXCHANGING)
                    await self.notifications_manager.notify_player(request.conn, current_player)
                case TurnAction.ASSASSINATE:
                    target = await game.get_target_player()
                    if target is None:
                        raise Exception("Find a better exception...")
                    await self._add_log_message(
                        game, f"{current_player.row.name} succesfully assasinated {target.row.name}"
                    )
                    await game.update(
                        turn_state=TurnState.TARGET_REVEALING,
                    )

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def reveal_influence(self, request: Request, influence: Influence) -> None:
        # This is all horrible, must refactor... writing this makes me feel better in the meantime
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

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

        if game.row.turn_state == TurnState.CHALLENGED:
            action = game.row.turn_action
            match action:
                case TurnAction.TAX:
                    if influence == Influence.DUKE:
                        await self._add_log_message(game, f"{player.row.name} succesfully took Tax")
                        await player.increment_coins(amount=3)
                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                        await game.update(
                            turn_state=TurnState.CHALLENGER_REVEALING,
                        )
                    else:
                        await self._next_player_turn(game)
                case TurnAction.STEAL:
                    if influence == Influence.CAPTAIN:
                        target = await game.get_target_player()
                        if target is None:
                            raise Exception("Whoa, where's the target!?")
                        await self._add_log_message(game, f"{player.row.name} succesfully stole from {target.row.name}")
                        await player.increment_coins(amount=2)
                        await target.decrement_coins(amount=2)

                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                        await game.update(
                            turn_state=TurnState.CHALLENGER_REVEALING,
                        )
                    else:
                        await self._next_player_turn(game)
                case TurnAction.EXCHANGE:
                    if influence == Influence.AMBASSADOR:
                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                        await game.update(
                            turn_state=TurnState.CHALLENGER_REVEALING,
                        )
                    else:
                        await self._next_player_turn(game)
                    pass
                case TurnAction.ASSASSINATE:
                    if influence == Influence.ASSASSIN:
                        target = await game.get_target_player()
                        if target is None:
                            raise Exception("Whoa, where's the target!?")
                        await self._add_log_message(
                            game, f"{player.row.name} succesfully assasinated {target.row.name}"
                        )
                        await game.update(
                            turn_state=TurnState.CHALLENGER_REVEALING,
                        )
                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                    else:
                        await self._next_player_turn(game)
                case _:
                    raise Exception("Unexpected challenge")

        elif game.row.turn_state == TurnState.BLOCK_CHALLENGED:
            action = game.row.turn_action
            match action:
                case TurnAction.FOREIGN_AID:
                    if influence == Influence.DUKE:
                        await self._add_log_message(game, f"{player.row.name} succesfully blocked Foreign Aid")
                        await game.update(turn_state=TurnState.BLOCK_CHALLENGER_REVEALING)

                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                    else:
                        await self._add_log_message(game, f"{current_player.row.name} succesfully took Foreign Aid")
                        await current_player.increment_coins(amount=2)
                        await self._next_player_turn(game)

                case TurnAction.STEAL:
                    target = await game.get_target_player()
                    if target is None:
                        raise Exception("Target missing")

                    if influence in {Influence.AMBASSADOR, Influence.CAPTAIN}:
                        await self._add_log_message(game, f"{player.row.name} succesfully blocked Foreign Aid")
                        await game.update(turn_state=TurnState.BLOCK_CHALLENGER_REVEALING)

                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                    else:
                        await self._add_log_message(
                            game, f"{current_player.row.name} succesfully stole from {target.row.name}"
                        )
                        await current_player.increment_coins(amount=2)
                        await target.decrement_coins(amount=2)
                        await self._next_player_turn(game)

                case TurnAction.ASSASSINATE:
                    target = await game.get_target_player()
                    if target is None:
                        raise Exception("Target missing")

                    if influence == Influence.CONTESSA:
                        await self._add_log_message(game, f"{player.row.name} succesfully blocked Assassination")
                        await game.update(turn_state=TurnState.BLOCK_CHALLENGER_REVEALING)

                        await game.return_to_deck([influence])
                        new_card = await game.take_from_deck(n=1)
                        match revealed:
                            case "A":
                                await player.update(influence_a=new_card[0], revealed_influence_a=False)
                            case "B":
                                await player.update(influence_b=new_card[0], revealed_influence_b=False)
                    else:
                        await self._add_log_message(
                            game, f"{current_player.row.name} succesfully assassinates {target.row.name}"
                        )
                        await game.update(turn_state=TurnState.TARGET_REVEALING)

                case _:
                    raise Exception("Unexpected block challenge")

        elif game.row.turn_state == TurnState.CHALLENGER_REVEALING:
            if game.row.turn_action == TurnAction.ASSASSINATE:
                await game.update(
                    turn_state=TurnState.TARGET_REVEALING,
                )
            elif game.row.turn_action == TurnAction.EXCHANGE:
                await game.update(
                    turn_state=TurnState.EXCHANGING,
                )

                await self.notifications_manager.notify_player(request.conn, current_player)
            else:
                await self._next_player_turn(game)
        else:
            await self._next_player_turn(game)

        if player.is_out:
            await self._add_log_message(game, f"{player.row.name} is out of the game!")

        players_remaining = [p for p in await game.get_players() if not p.is_out]
        if len(players_remaining) == 1:
            winner = players_remaining[0]
            await self._add_log_message(game, f"{winner.row.name} wins the game!")
            await game.update(state=GameState.FINISHED, winner_id=winner.id)

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)
        # In case the hand changed...
        await self.notifications_manager.notify_player(request.conn, player)

    async def challenge(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

        game = await player.get_game()

        if game.row.turn_state != TurnState.ATTEMPTED:
            raise Exception("Invalid turn state")

        if game.row.player_turn_id == player.id:
            raise Exception("Cannot challenge self")

        if game.row.turn_action in {
            TurnAction.INCOME,
            TurnAction.FOREIGN_AID,
            TurnAction.COUP,
        }:
            raise Exception("Cannot challenge this action")

        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("Get a better exception..")

        await self._add_log_message(game, f"{player.row.name} challenges {current_player.row.name}")
        await game.update(turn_state=TurnState.CHALLENGED, challenged_by_id=player.id)
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def block(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

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

        if game.row.turn_action not in {
            TurnAction.FOREIGN_AID,
            TurnAction.ASSASSINATE,
            TurnAction.STEAL,
        }:
            raise Exception("Cannot block current action")

        await game.update(turn_state=TurnState.BLOCKED, blocked_by_id=player.id)
        await self._add_log_message(game, f"{player.row.name} blocks {current_player.row.name}")
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def accept_block(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

        game = await player.get_game()
        if player.id != game.row.player_turn_id:
            raise Exception("Current turn player can only accept blocks")

        await self._add_log_message(game, f"{player.row.name} backs down")
        await self._next_player_turn(game)
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def challenge_block(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

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
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

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
        await self._next_player_turn(game)

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)
        await self.notifications_manager.notify_player(request.conn, player)
