import random
import string
from sqlite3 import IntegrityError
from typing import Tuple

from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.games import GameRow, GamesTable
from coup_clone.db.players import Influence, PlayerRow, PlayersTable
from coup_clone.managers.session import ActiveSession

DECK = "aaammmcccdddppp"


class PlayerAlreadyInGameException(Exception):
    ...


class PlayerNotInGameException(Exception):
    ...


class GameNotFoundException(Exception):
    ...


def _player_json(player: PlayerRow) -> dict:
    return {
        "id": player.id,
        "name": player.name,
        "state": player.state,
        "coins": player.coins,
        "influence": [
            player.influence_a if player.revealed_influence_a else Influence.UNKNOWN,
            player.influence_b if player.revealed_influence_b else Influence.UNKNOWN,
        ],
        "host": player.host,
    }


def _game_json(game: GameRow) -> dict:
    return {
        "id": game.id,
        "state": game.state,
        "currentPlayerTurn": None,
    }


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
                "game": _game_json(game),
                "players": [_player_json(p) for p in players],
                "currentPlayer": _player_json(player) if player is not None else None,
                "events": [],
            },
            room=session.session.id,
        )
