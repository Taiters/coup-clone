from aiosqlite import Connection
from socketio import AsyncNamespace
from socketio.exceptions import ConnectionRefusedError

from coup_clone import db
from coup_clone.managers.exceptions import (
    GameNotFoundException,
    PlayerAlreadyInGameException,
)
from coup_clone.managers.game import GameManager
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.managers.session import NoActiveSessionException, SessionManager
from coup_clone.session import ActiveSession


class Handler(AsyncNamespace):
    def __init__(
        self,
        session_manager: SessionManager,
        game_manager: GameManager,
        notifications_manager: NotificationsManager,
    ):
        self.session_manager = session_manager
        self.game_manager = game_manager
        self.notifications_manager = notifications_manager
        super().__init__()

    async def _get_session(self, conn: Connection, sid: str) -> ActiveSession:
        try:
            return await self.session_manager.get(conn, sid)
        except NoActiveSessionException:
            await self.disconnect(sid)
            raise

    async def on_connect(self, sid: str, environ: dict, auth: dict) -> None:
        print("on_connect: ", sid)
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

    async def on_create_game(self, sid: str) -> None:
        print("on_create_game: ", sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            try:
                await self.game_manager.create(conn, session)
            except PlayerAlreadyInGameException:
                await self.disconnect(sid)
                raise

    async def on_join_game(self, sid: str, game_id: str) -> None:
        print("on_join_game: ", sid, game_id)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            try:
                await self.game_manager.join(conn, game_id, session)
            except (PlayerAlreadyInGameException, GameNotFoundException):
                await self.disconnect(sid)
                raise

    async def on_leave_game(self, sid: str) -> None:
        print("on_leave_game: ", sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.leave(conn, session)

    async def on_initialize_game(self, sid: str) -> None:
        print("on_initialize_game: ", sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.notifications_manager.notify_game_full(conn, session)

    async def on_set_name(self, sid: str, name: str) -> None:
        print("on_set_name: ", sid, name)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.set_name(conn, session, name)

    async def on_start_game(self, sid: str) -> None:
        print("on_start_game: ", sid)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.start(conn, session)

    async def on_take_action(self, sid: str, action: dict) -> None:
        print("on_take_action: ", sid, action)
        async with db.open() as conn:
            session = await self._get_session(conn, sid)
            await self.game_manager.take_action(conn, session, action["action"], action.get("target", None))
