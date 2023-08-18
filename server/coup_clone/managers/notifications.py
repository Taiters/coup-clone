from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.events import EventRow, EventsTable
from coup_clone.db.games import GameRow, GamesTable
from coup_clone.db.players import Influence, PlayerRow, PlayersTable
from coup_clone.managers.exceptions import PlayerNotInGameException
from coup_clone.session import ActiveSession


def map_session(session: ActiveSession) -> dict:
    return {"id": session.id, "player_id": session.session.player_id}


def map_player(player: PlayerRow) -> dict:
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


def map_event(event: EventRow) -> dict:
    return {
        "id": event.id,
        "timestamp": event.time_created.timestamp(),
        "actor_id": event.actor_id,
        "message": event.message,
    }


def map_game(game: GameRow) -> dict:
    return {
        "id": game.id,
        "state": game.state,
        "player_turn_id": game.player_turn_id,
        "turn_state_modified": game.turn_state_modified.timestamp() if game.turn_state_modified is not None else None,
        "turn_state_deadline": game.turn_state_deadline.timestamp() if game.turn_state_deadline is not None else None,
    }


class NotificationsManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        games_table: GamesTable,
        players_table: PlayersTable,
        events_table: EventsTable,
    ):
        self.socket_server = socket_server
        self.games_table = games_table
        self.players_table = players_table
        self.events_table = events_table

    async def notify_session(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
        await self.socket_server.emit(
            "session",
            {
                "session": map_session(session),
                "game_id": current_player.game_id if current_player else None,
            },
            room=session.session.id,
        )

    async def notify_game_full(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            game = await self.games_table.get(cursor, player.game_id)
            players = await self.players_table.query(cursor, game_id=game.id)
            events = await self.events_table.query(cursor, game_id=game.id)

        await self.socket_server.emit(
            "game:all",
            {
                "game": map_game(game),
                "players": [map_player(p) for p in players],
                "events": [map_event(e) for e in events],
                "hand": [
                    player.influence_a,
                    player.influence_b,
                ],
            },
            room=session.session.id,
        )

    async def broadcast_game(self, conn: Connection, game_id: str) -> None:
        async with conn.cursor() as cursor:
            game = await self.games_table.get(cursor, game_id)
        await self.socket_server.emit(
            "game:game",
            map_game(game),
            room=game_id,
        )

    async def broadcast_game_players(self, conn: Connection, game_id: str) -> None:
        async with conn.cursor() as cursor:
            players = await self.players_table.query(cursor, game_id=game_id)
        await self.socket_server.emit(
            "game:players",
            [map_player(p) for p in players],
            room=game_id,
        )

    async def broadcast_game_events(self, conn: Connection, game_id: str) -> None:
        async with conn.cursor() as cursor:
            events = await self.events_table.query(cursor, game_id=game_id)
        await self.socket_server.emit(
            "game:events",
            [map_event(e) for e in events],
            room=game_id,
        )
