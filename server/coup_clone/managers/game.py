import random
import string
from sqlite3 import IntegrityError
from typing import Tuple

from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.games import GamesTable
from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.session import ActiveSession
from coup_clone.mappers import map_game, map_player

DECK = "aaammmcccdddppp"


class PlayerAlreadyInGameException(Exception):
    ...


class PlayerNotInGameException(Exception):
    ...


class GameNotFoundException(Exception):
    ...


class GameManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        games_table: GamesTable,
        players_table: PlayersTable,
    ):
        self.socket_server = socket_server
        self.games_table = games_table
        self.players_table = players_table

    async def create(self, conn: Connection, session: ActiveSession) -> Tuple[str, PlayerRow]:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
            if current_player is not None:
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

            game_id = "".join([random.choice(string.ascii_lowercase) for _ in range(6)])
            game = await self.games_table.create(cursor, id=game_id, deck="".join(random.sample(DECK, k=len(DECK))))
            player = await self.players_table.create(cursor, game_id=game.id)
            await session.set_current_player(cursor, player.id)
            await conn.commit()
        self.socket_server.enter_room(session.sid, game.id)
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
        return (game_id, player)

    async def leave(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is not None:
                await session.clear_current_player(cursor)
                await conn.commit()
                self.socket_server.leave_room(session.sid, player.game_id)

    async def notify(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException("Attempted to notify player when not in game")
            game = await self.games_table.get(cursor, player.game_id)
            players = await self.players_table.query(cursor, game_id=game.id)

        await self.socket_server.emit(
            "game",
            {
                "game": map_game(game),
                "players": [map_player(p, session) for p in players],
                "events": [],
            },
            room=session.session.id,
        )
