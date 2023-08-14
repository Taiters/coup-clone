from aiosqlite import Connection
from socketio import AsyncNamespace
from socketio.exceptions import ConnectionRefusedError

from coup_clone import db
from coup_clone.managers.game import (
    GameManager,
    GameNotFoundException,
    PlayerAlreadyInGameException,
)
from coup_clone.managers.session import (
    ActiveSession,
    NoActiveSessionException,
    SessionManager,
)


class Handler(AsyncNamespace):
    def __init__(
        self,
        session_manager: SessionManager,
        game_manager: GameManager,
    ):
        self.session_manager = session_manager
        self.game_manager = game_manager
        super().__init__()

    async def _get_session(self, conn: Connection, sid: str) -> ActiveSession:
        try:
            return await self.session_manager.get(conn, sid)
        except NoActiveSessionException:
            await self.disconnect(sid)
            raise

    async def on_connect(self, sid: str, environ: dict, auth: dict) -> None:
        async with db.open() as conn:
            session = await self.session_manager.setup(conn, sid, auth)
            game = auth.get("game", None) if auth else None
            if game:
                try:
                    await self.game_manager.join(conn, game, session)
                except (PlayerAlreadyInGameException, GameNotFoundException):
                    raise ConnectionRefusedError('invalid game id')
            await self.session_manager.notify(conn, session)

    async def on_create_game(self, sid: str) -> None:
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            try:
                await self.game_manager.create(conn, session)
            except PlayerAlreadyInGameException:
                await self.disconnect(sid)
                raise
            await self.session_manager.notify(conn, session)

    async def on_join_game(self, sid: str, game_id: str) -> None:
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            try:
                await self.game_manager.join(conn, game_id, session)
            except (PlayerAlreadyInGameException, GameNotFoundException):
                await self.disconnect(sid)
                raise
            await self.session_manager.notify(conn, session)

    async def on_leave_game(self, sid: str) -> None:
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.leave(conn, session)
            await self.session_manager.notify(conn, session)

    async def on_initialize_game(self, sid: str) -> None:
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.notify(conn, session)
