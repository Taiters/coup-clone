import random
import string
from sqlite3 import IntegrityError
from typing import Tuple

from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.games import GamesTable
from coup_clone.db.players import PlayerRow, PlayersTable, PlayerState
from coup_clone.managers.exceptions import (
    GameNotFoundException,
    PlayerAlreadyInGameException,
    PlayerNotInGameException,
)
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.session import ActiveSession

DECK = "aaammmcccdddppp"


class GameManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        notifications_manager: NotificationsManager,
        games_table: GamesTable,
        players_table: PlayersTable,
    ):
        self.socket_server = socket_server
        self.notifications_manager = notifications_manager
        self.games_table = games_table
        self.players_table = players_table

    async def create(self, conn: Connection, session: ActiveSession) -> Tuple[str, PlayerRow]:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
            if current_player is not None:
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

            game_id = "".join([random.choice(string.ascii_lowercase) for _ in range(6)])
            game = await self.games_table.create(cursor, id=game_id, deck="".join(random.sample(DECK, k=len(DECK))))
            player = await self.players_table.create(cursor, game_id=game.id, host=True)
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

            try:
                player = await self.players_table.create(cursor, game_id=game_id)
                await session.set_current_player(cursor, player.id)
                await conn.commit()
            except IntegrityError as e:
                if str(e) == "FOREIGN KEY constraint failed":
                    raise GameNotFoundException("Game not found with ID: " + game_id)
                raise
        self.socket_server.enter_room(session.sid, game_id)
        await self.notifications_manager.broadcast_game_players(conn, game_id, session)
        await self.notifications_manager.notify_session(conn, session)
        return (game_id, player)

    async def leave(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is not None:
                await session.clear_current_player(cursor)
                await conn.commit()
                self.socket_server.leave_room(session.sid, player.game_id)
                await self.notifications_manager.broadcast_game_players(conn, player.game_id, session)
        await self.notifications_manager.notify_session(conn, session)

    async def set_name(self, conn: Connection, session: ActiveSession, name: str) -> None:
        async with conn.cursor() as cursor:
            player_id = session.session.player_id
            if player_id is None:
                raise PlayerNotInGameException()
            await self.players_table.update(cursor, player_id, name=name, state=PlayerState.READY)
            await conn.commit()
            player = await session.current_player(cursor)
        await self.notifications_manager.broadcast_game_players(conn, player.game_id, session)
