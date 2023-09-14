from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.events import EventRow, EventsTable
from coup_clone.db.games import GameRow, GamesTable, TurnState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable
from coup_clone.models import Game, Player, Session
from coup_clone.request import Request


def map_session(session: Session) -> dict:
    return {"id": session.id, "player_id": session.player_id}


def map_player(player: PlayerRow) -> dict:
    return {
        "id": player.id,
        "name": player.name,
        "state": player.state,
        "coins": player.coins,
        "influence_a": player.influence_a if player.revealed_influence_a else Influence.UNKNOWN,
        "influence_b": player.influence_b if player.revealed_influence_b else Influence.UNKNOWN,
        "host": player.host,
        "accepts_action": player.accepts_action,
    }


def map_event(event: EventRow) -> dict:
    return {
        "id": event.id,
        "timestamp": event.time_created.timestamp(),
        "message": event.message,
    }


def map_game(game: GameRow) -> dict:
    return {
        "id": game.id,
        "state": game.state,
        "player_turn_id": game.player_turn_id,
        "turn_action": game.turn_action,
        "turn_state": game.turn_state,
        "turn_state_modified": game.turn_state_modified.timestamp() if game.turn_state_modified is not None else None,
        "turn_state_deadline": game.turn_state_deadline.timestamp() if game.turn_state_deadline is not None else None,
        "turn_target": game.target_id,
        "turn_challenger": game.challenged_by_id,
        "turn_blocker": game.blocked_by_id,
        "turn_block_challenger": game.block_challenged_by_id,
        "winner": game.winner_id,
    }


class NotificationsManager:
    def __init__(
        self,
        socket_server: AsyncServer,
    ):
        self.socket_server = socket_server

    async def _send_game(self, conn: Connection, game_id: str, to: str) -> None:
        async with conn.cursor() as cursor:
            game = await GamesTable.get(cursor, game_id)
            if game is None:
                return
            players = await PlayersTable.query(cursor, game_id=game.id)
            events = await EventsTable.query(cursor, game_id=game.id)

        await self.socket_server.emit(
            "game",
            {
                "game": map_game(game),
                "players": [map_player(p) for p in players],
                "events": [map_event(e) for e in events],
            },
            room=to,
        )

    async def notify_session(self, session: Session) -> None:
        current_player = await session.get_player()
        await self.socket_server.emit(
            "session",
            {
                "session": map_session(session),
                "game_id": current_player.game_id if current_player else None,
            },
            room=session.id,
        )

    async def notify_player(self, conn: Connection, player: Player) -> None:
        session = await player.get_session()
        if session is None:
            raise Exception("No session to nofify")

        game = await Game.get(conn, player.game_id)
        if game is None:
            raise Exception("No game!")

        await self._send_game(conn, player.game_id, to=session.id)
        await self.socket_server.emit(
            "hand",
            {
                "influence_a": player.row.influence_a,
                "influence_b": player.row.influence_b,
                "top_of_deck": [Influence(int(i)) for i in game.row.deck[-2:]]
                if game.row.turn_state == TurnState.EXCHANGING and game.row.player_turn_id == player.id
                else [],
            },
            to=session.id,
        )

    async def notify_error(self, request: Request, title: str, message: str) -> None:
        await self.socket_server.emit(
            "error_msg",
            {
                "title": title,
                "message": message,
            },
            to=request.sid,
        )

    async def broadcast_game(self, conn: Connection, game_id: str) -> None:
        await self._send_game(conn, game_id, to=game_id)
