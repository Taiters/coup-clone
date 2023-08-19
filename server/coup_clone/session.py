from typing import Optional

from aiosqlite import Cursor

from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable


class ActiveSession:
    def __init__(
        self,
        sid: str,
        session: SessionRow,
    ):
        self.sid = sid
        self.session = session
        self._loaded_player = False

    async def current_player(self, cursor: Cursor) -> Optional[PlayerRow]:
        if self.session.player_id is None:
            return None
        return await PlayersTable.get(
            cursor,
            self.session.player_id,
        )

    async def set_current_player(self, cursor: Cursor, player_id: int) -> None:
        await SessionsTable.update(cursor, self.session.id, player_id=player_id)
        self.session.player_id = player_id

    async def clear_current_player(self, cursor: Cursor) -> None:
        if self.session.player_id is None:
            return
        await PlayersTable.delete(
            cursor,
            self.session.player_id,
        )
        self.session.player_id = None

    @property
    def id(self) -> str:
        return self.session.id

    @property
    def player_id(self) -> Optional[int]:
        return self.session.player_id
