from uuid import uuid4

from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.players import PlayersTable
from coup_clone.db.sessions import SessionsTable
from coup_clone.mappers import map_session
from coup_clone.session import ActiveSession

SESSION_KEY = "session"


class NoActiveSessionException(Exception):
    ...


class SessionManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        sessions_table: SessionsTable,
        players_table: PlayersTable,
    ):
        self.socket_server = socket_server
        self.sessions_table = sessions_table
        self.players_table = players_table

    async def setup(self, conn: Connection, sid: str, auth: dict) -> ActiveSession:
        async with self.socket_server.session(sid) as socket_session:
            session = None
            session_id = auth.get(SESSION_KEY, None) if auth else None

            async with conn.cursor() as cursor:
                if session_id:
                    session = await self.sessions_table.get(cursor, session_id)

                if session is None:
                    session = await self.sessions_table.create(cursor, id=str(uuid4()))
                    await conn.commit()

                socket_session[SESSION_KEY] = session.id

                active_session = ActiveSession(
                    sid,
                    session,
                    self.sessions_table,
                    self.players_table,
                )

        self.socket_server.enter_room(sid, session.id)
        return active_session

    async def get(self, conn: Connection, sid: str) -> ActiveSession:
        async with self.socket_server.session(sid) as socket_session:
            session_id = socket_session.get(SESSION_KEY, None)

        if session_id is None:
            raise NoActiveSessionException("session is not present in socket connection")

        async with conn.cursor() as cursor:
            existing_session = await self.sessions_table.get(cursor, session_id)

        if existing_session is None:
            raise NoActiveSessionException("session not found in database")

        return ActiveSession(
            sid,
            existing_session,
            self.sessions_table,
            self.players_table,
        )

    async def notify(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
        await self.socket_server.emit(
            "session",
            {
                "session": map_session(session),
                "gameID": current_player.game_id if current_player else None,
            },
            room=session.session.id,
        )
