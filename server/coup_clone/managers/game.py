import random
import string
from sqlite3 import IntegrityError
from typing import Optional, Tuple

from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.actions import Action, ForeignAid, Income, Tax
from coup_clone.db.games import GamesTable, GameState, TurnAction, TurnState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable, PlayerState
from coup_clone.managers.exceptions import (
    GameFullException,
    GameNotFoundException,
    NotEnoughPlayersException,
    NotPlayerTurnException,
    PlayerAlreadyInGameException,
    PlayerNotInGameException,
    UnsupportedActionException,
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


class GameManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        notifications_manager: NotificationsManager,
    ):
        self.socket_server = socket_server
        self.notifications_manager = notifications_manager

    async def _next_player_turn(self, game: Game) -> None:
        next_player = await game.get_next_player_turn()
        await game.reset_turn_state(next_player.id)

    def _get_action(self, conn: Connection, request: Request, action: TurnAction, target: Optional[int]) -> Action:
        match action:
            case TurnAction.INCOME:
                return Income(conn, request)
            case TurnAction.FOREIGN_AID:
                return ForeignAid(conn, request)
            case TurnAction.TAX:
                return Tax(conn, request)
            case _:
                raise UnsupportedActionException("Unsupported action: " + str(action))

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
        if player is not None:
            game = await player.get_game()
            await game.return_to_deck([player.influence_a, player.influence_b])
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
            await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def take_action(self, request: Request, turn_action: TurnAction, target: Optional[int]) -> None:
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
            case TurnAction.FOREIGN_AID:
                await game.update(
                    turn_action=TurnAction.FOREIGN_AID,
                    turn_state=TurnState.ATTEMPTED,
                )
            case TurnAction.TAX:
                await game.update(
                    turn_action=TurnAction.TAX,
                    turn_state=TurnState.ATTEMPTED,
                )
            case TurnAction.STEAL:
                await game.update(
                    turn_action=TurnAction.STEAL,
                    turn_state=TurnState.ATTEMPTED,
                    target_id=target,
                )
            case TurnAction.EXCHANGE:
                await game.update(
                    turn_action=TurnAction.EXCHANGE,
                    turn_state=TurnState.ATTEMPTED,
                )
            case TurnAction.ASSASSINATE:
                await game.update(
                    turn_action=TurnAction.ASSASSINATE,
                    turn_state=TurnState.ATTEMPTED,
                    target_id=target,
                )
            case TurnAction.COUP:
                await game.update(
                    turn_action=TurnAction.COUP,
                    turn_state=TurnState.TARGET_REVEALING,
                    target_id=target,
                )
        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)

    async def accept_action(self, request: Request) -> None:
        player = await request.session.get_player()
        if player is None:
            raise PlayerNotInGameException()

        await player.update(accepts_action=True)

        game = await player.get_game()

        all_players_accepted = await game.all_players_accepted()
        if not all_players_accepted:
            return None

        current_player = await game.get_current_player()
        if current_player is None:
            raise Exception("Get a better exception..")

        match game.row.turn_action:
            case TurnAction.FOREIGN_AID:
                await current_player.increment_coins(amount=2)
                await self._next_player_turn(game)
            case TurnAction.TAX:
                await current_player.increment_coins(amount=3)
                await self._next_player_turn(game)
            case TurnAction.STEAL:
                target = await game.get_target_player()
                if target is None:
                    raise Exception("Find a better exception...")
                await current_player.increment_coins(amount=2)
                await target.decrement_coins(amount=2)
                await self._next_player_turn(game)
            case TurnAction.EXCHANGE:
                # TODO: something
                pass
            case TurnAction.ASSASSINATE:
                await game.update(
                    turn_state=TurnState.TARGET_REVEALING,
                )

        await request.conn.commit()
        await self.notifications_manager.broadcast_game(request.conn, player.game_id)
