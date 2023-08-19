import random
import string
from sqlite3 import IntegrityError
from typing import Optional, Tuple

from aiosqlite import Connection, Cursor
from socketio import AsyncServer

from coup_clone.actions import Action, ForeignAid, Income, Tax
from coup_clone.db.games import GamesTable, GameState, TurnAction
from coup_clone.db.players import Influence, PlayerRow, PlayersTable, PlayerState
from coup_clone.managers.exceptions import (
    GameFullException,
    NotEnoughPlayersException,
    NotPlayerTurnException,
    PlayerAlreadyInGameException,
    PlayerNotInGameException,
    UnsupportedActionException,
)
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.session import ActiveSession

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

    async def _next_player_turn(self, cursor: Cursor, game_id: str) -> None:
        game = await GamesTable.get(cursor, game_id)
        next_player = await PlayersTable.get_next_player_turn(cursor, game_id, game.player_turn_id)
        await GamesTable.reset_turn_state(cursor, game.id, next_player.id)

    def _get_action(self, session: ActiveSession, action: TurnAction, target: Optional[int]) -> Action:
        match action:
            case TurnAction.INCOME:
                return Income(session)
            case TurnAction.FOREIGN_AID:
                return ForeignAid(session)
            case TurnAction.TAX:
                return Tax(session)
            case _:
                raise UnsupportedActionException("Unsupported action: " + str(action))

    async def create(self, conn: Connection, session: ActiveSession) -> Tuple[str, PlayerRow]:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
            if current_player is not None:
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

            game_id = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
            game = await GamesTable.create(
                cursor, id=game_id, deck="".join(str(c.value) for c in random.sample(DECK, k=len(DECK)))
            )
            hand = await GamesTable.take_from_deck(cursor, game_id)
            player = await PlayersTable.create(
                cursor, game_id=game.id, host=True, influence_a=hand[0], influence_b=hand[1]
            )
            await GamesTable.update(cursor, game.id, player_turn_id=player.id)
            await session.set_current_player(cursor, player.id)
            await conn.commit()
        self.socket_server.enter_room(session.sid, game.id)
        await self.notifications_manager.notify_session(conn, session)
        return (game.id, player)

    async def join(self, conn: Connection, game_id: str, session: ActiveSession) -> Tuple[str, PlayerRow]:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
            if current_player is not None:
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

            hand = await GamesTable.take_from_deck(cursor, game_id)
            try:
                player = await PlayersTable.create(cursor, game_id=game_id, influence_a=hand[0], influence_b=hand[1])
            except IntegrityError as e:
                if str(e) == "Game full":
                    raise GameFullException()
            await session.set_current_player(cursor, player.id)
            await conn.commit()

        self.socket_server.enter_room(session.sid, game_id)
        await self.notifications_manager.broadcast_game(conn, game_id)
        await self.notifications_manager.notify_session(conn, session)
        return (game_id, player)

    async def leave(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is not None:
                await GamesTable.return_to_deck(cursor, player.game_id, [player.influence_a, player.influence_b])
                await session.clear_current_player(cursor)
                await conn.commit()
                self.socket_server.leave_room(session.sid, player.game_id)
                await self.notifications_manager.broadcast_game(conn, player.game_id)
        await self.notifications_manager.notify_session(conn, session)

    async def set_name(self, conn: Connection, session: ActiveSession, name: str) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            await PlayersTable.update(cursor, player.id, name=name, state=PlayerState.READY)
            await conn.commit()
        await self.notifications_manager.broadcast_game(conn, player.game_id)

    async def start(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            player_count = await PlayersTable.count(cursor, game_id=player.game_id, state=PlayerState.READY)
            if player_count < 2:
                raise NotEnoughPlayersException()
            await GamesTable.update(cursor, player.game_id, state=GameState.RUNNING)
            await self._next_player_turn(cursor, player.game_id)
            await conn.commit()
        await self.notifications_manager.broadcast_game(conn, player.game_id)

    async def take_action(
        self, conn: Connection, session: ActiveSession, turn_action: TurnAction, target: Optional[int]
    ) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            game = await GamesTable.get(cursor, player.game_id)
            if game.player_turn_id != player.id:
                raise NotPlayerTurnException()
            action = self._get_action(session, turn_action, target)
            turn_complete = await action.execute(cursor)
            if turn_complete:
                await self._next_player_turn(cursor, game.id)
            await conn.commit()
        await self.notifications_manager.broadcast_game(conn, player.game_id)
