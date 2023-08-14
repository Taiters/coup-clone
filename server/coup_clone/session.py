from sqlite3 import Cursor
from typing import Optional
from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable


class ActiveSession:
    def __init__(
        self,
        sid: str,
        session: SessionRow,
        sessions_table: SessionsTable,
        players_table: PlayersTable,
    ):
        self.sid = sid
        self.session = session
        self.sessions_table = sessions_table
        self.players_table = players_table
        self._loaded_player = False

    async def current_player(self, cursor: Cursor) -> Optional[PlayerRow]:
        if self.session.player_id is None:
            return None
        return await self.players_table.get(
            cursor,
            self.session.player_id,
        )

    async def set_current_player(self, cursor: Cursor, player_id: int) -> None:
        await self.sessions_table.update(cursor, self.session.id, player_id=player_id)
        self.session.player_id = player_id

    async def clear_current_player(self, cursor: Cursor) -> None:
        if self.session.player_id is None:
            return
        await self.players_table.delete(
            cursor,
            self.session.player_id,
        )
        self.session.player_id = None

    @property
    def id(self) -> str:
        return self.session.id

