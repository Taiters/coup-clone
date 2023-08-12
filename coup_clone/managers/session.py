from contextlib import asynccontextmanager
from sqlite3 import Cursor
from uuid import uuid4
from engineio import AsyncServer
from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable


SESSION_KEY = 'session'


class ActiveSession:
    def __init__(
        self,
        session: SessionRow,
        sessions_table: SessionsTable,
        players_table: PlayersTable,
        cursor: Cursor,
    ):
        self.session = session
        self.sessions_table = sessions_table
        self.players_table = players_table
        self.cursor = cursor

    
    async def current_player(self) -> PlayerRow:
        if self.session.player_id is None:
            return None
        return await self.players_table.get(
            self.cursor,
            self.session.player_id,
        )
    
    async def set_current_player(self, player_id: int) -> None:
        await self.sessions_table.update(
            self.cursor,
            self.session.id,
            player_id=player_id
        )
    
    async def clear_current_player(self) -> None:
        await self.sessions_table.update(
            self.cursor,
            self.session.id,
            player_id=None
        )
        
        
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
    
    
    async def setup_session(self, cursor: Cursor, sid: str, auth: dict) -> ActiveSession:
        async with self.socket_server.session(sid) as socket_session:
            session = None
            session_id = auth.get(SESSION_KEY, None) if auth else None

            if session_id:
                session = await self.sessions_table.get(cursor, session_id)

            if session is None:
                session = await self.sessions_table.create(cursor, id=str(uuid4()))
            
            socket_session[SESSION_KEY] = session.id

        active_session = ActiveSession(
            session,
            self.sessions_table,
            self.players_table,
            cursor
        )
        current_player = await active_session.current_player()

        self.socket_server.enter_room(sid, session.id)
        await self.emit(
            'session',
            {
                'sessionID': session.id,
                'currentGameID': current_player.game_id if current_player else None,
            },
            room=session.id,
        )
        return active_session
    

    async def get_session(self, cursor: Cursor, sid: str) -> ActiveSession:
        async with self.socket_server.session(sid) as socket_session:
            session_id = socket_session[SESSION_KEY]

        if session_id is None:
            await self.socket_server.disconnect(sid)
            raise ValueError('session is not present in socket connection')

        existing_session = self.sessions_table.get(cursor, session_id)
        if existing_session is None:
            await self.socket_server.disconnect(sid)
            raise ValueError('session not found in database')
        
        return ActiveSession(
            existing_session,
            self.sessions_table,
            self.players_table,
            cursor
        )
