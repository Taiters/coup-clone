from aiosqlite import Connection
from socketio import AsyncNamespace
from socketio.exceptions import ConnectionRefusedError

from coup_clone import db
from coup_clone.managers.game import (
    GameManager,
    GameNotFoundException,
    PlayerAlreadyInGameException,
)
from coup_clone.managers.session import NoActiveSessionException, SessionManager
from coup_clone.session import ActiveSession


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
        print('on_connect: ', sid)
        async with db.open() as conn:
            session = await self.session_manager.setup(conn, sid, auth)
            game = auth.get("game", None) if auth else None
            if game:
                async with conn.cursor() as cursor:
                    player = await session.current_player(cursor)
                if player:
                    if player.game_id != game:
                        raise ConnectionRefusedError("invalid game id")
                else:
                    try:
                        await self.game_manager.join(conn, game, session)
                    except GameNotFoundException:
                        raise ConnectionRefusedError("invalid game id")
            await self.session_manager.notify(conn, session)

    async def on_create_game(self, sid: str) -> None:
        print('on_create_game: ', sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            try:
                await self.game_manager.create(conn, session)
            except PlayerAlreadyInGameException:
                await self.disconnect(sid)
                raise
            await self.session_manager.notify(conn, session)

    async def on_join_game(self, sid: str, game_id: str) -> None:
        print('on_join_game: ', sid, game_id)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            try:
                await self.game_manager.join(conn, game_id, session)
            except (PlayerAlreadyInGameException, GameNotFoundException):
                await self.disconnect(sid)
                raise
            await self.session_manager.notify(conn, session)
            await self.game_manager.notify_players(conn, session)

    async def on_leave_game(self, sid: str) -> None:
        print('on_leave_game: ', sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.leave(conn, session)
            await self.session_manager.notify(conn, session)

    async def on_initialize_game(self, sid: str) -> None:
        print('on_initialize_game: ', sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.notify_all(conn, session)

    async def on_set_name(self, sid: str, name: str) -> None:
        print('on_set_name: ', sid, name)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.set_name(conn, session, name)
            await self.game_manager.notify_players(conn, session)
