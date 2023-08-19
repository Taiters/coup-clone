from uuid import uuid4

from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.sessions import SessionsTable
from coup_clone.managers.exceptions import NoActiveSessionException
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.models import Session

SESSION_KEY = "session"


class SessionManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        notifications_manager: NotificationsManager,
    ):
        self.socket_server = socket_server
        self.notifications_manager = notifications_manager

    async def setup(self, conn: Connection, sid: str, auth: dict) -> Session:
        async with self.socket_server.session(sid) as socket_session:
            session = None
            session_id = auth.get(SESSION_KEY, None) if auth else None

            async with conn.cursor() as cursor:
                if session_id:
                    session = await SessionsTable.get(cursor, session_id)

                if session is None:
                    session = await SessionsTable.create(cursor, id=str(uuid4()))
                    await conn.commit()

                socket_session[SESSION_KEY] = session.id

                active_session = Session(cursor, session)
                current_player = await active_session.get_player()
                if current_player:
                    self.socket_server.enter_room(sid, current_player.game_id)

        self.socket_server.enter_room(sid, session.id)
        await self.notifications_manager.notify_session(active_session)
        return active_session

    async def get(self, conn: Connection, sid: str) -> ActiveSession:
        async with self.socket_server.session(sid) as socket_session:
            session_id = socket_session.get(SESSION_KEY, None)

        if session_id is None:
            raise NoActiveSessionException("session is not present in socket connection")

        async with conn.cursor() as cursor:
            existing_session = await SessionsTable.get(cursor, session_id)

        if existing_session is None:
            raise NoActiveSessionException("session not found in database")

        return ActiveSession(
            sid,
            existing_session,
        )
