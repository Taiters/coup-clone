import functools
import traceback
from typing import Any, Callable

from socketio import AsyncNamespace
from socketio.exceptions import ConnectionRefusedError

from coup_clone import db
from coup_clone.db.players import Influence
from coup_clone.managers.exceptions import (
    GameNotFoundException,
    PlayerAlreadyInGameException,
    UserException,
)
from coup_clone.managers.game import ExchangeInfluence, GameManager
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.managers.session import NoActiveSessionException, SessionManager
from coup_clone.request import Request


def with_request(f: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(f)
    async def wrapper(self: "Handler", sid: str, *args: Any) -> None:
        async with db.open() as conn:
            try:
                session = await self.session_manager.get(conn, sid)
                await f(
                    self,
                    Request(
                        sid=sid,
                        conn=conn,
                        session=session,
                    ),
                    *args
                )
            except NoActiveSessionException:
                raise

    return wrapper

def socket_response(f: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(f)
    async def wrapper(self: "Handler", *args: Any) -> None:
            try:
                await f(
                    self,
                    *args,
                )
                return {
                    "status": "success",
                }
            except UserException as e:
                traceback.print_exc()
                return {
                    "status": "error",
                    "error": e.as_error_response()     
                }

    return wrapper


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

    async def on_connect(self, sid: str, environ: dict, auth: dict) -> None:
        print("on_connect: ", sid)
        async with db.open() as conn:
            session = await self.session_manager.setup(conn, sid, auth)
            game = auth.get("game", None) if auth else None
            if game:
                player = await session.get_player()
                if player:
                    if player.game_id != game:
                        raise ConnectionRefusedError("invalid game id")
                else:
                    try:
                        await self.game_manager.join(Request(sid, conn=conn, session=session), game)
                    except GameNotFoundException:
                        raise ConnectionRefusedError("invalid game id")

    @with_request
    async def on_create_game(self, request: Request) -> None:
        print("on_create_game: ", request.sid)
        try:
            await self.game_manager.create(request)
        except PlayerAlreadyInGameException:
            await self.disconnect(request.sid)
            raise

    @socket_response
    @with_request
    async def on_join_game(self, request: Request, game_id: str) -> None:
        print("on_join_game: ", request.sid, game_id)
        try:
            await self.game_manager.join(request, game_id.lower())
        except (PlayerAlreadyInGameException, GameNotFoundException):
            raise

    @with_request
    async def on_leave_game(self, request: Request) -> None:
        print("on_leave_game: ", request.sid)
        await self.game_manager.leave(request)

    @with_request
    async def on_initialize_game(self, request: Request) -> None:
        print("on_initialize_game: ", request.sid)
        player = await request.session.get_playerX()
        await self.notifications_manager.notify_player(request.conn, player)

    @with_request
    async def on_set_name(self, request: Request, name: str) -> None:
        print("on_set_name: ", request.sid, name)
        await self.game_manager.set_name(request, name)

    @with_request
    async def on_start_game(self, request: Request) -> None:
        print("on_start_game: ", request.sid)
        await self.game_manager.start(request)

    @with_request
    async def on_take_action(self, request: Request, action: dict) -> None:
        print("on_take_action: ", request.sid, action)
        await self.game_manager.take_action(request, action["action"], action.get("target", None))

    @with_request
    async def on_accept_action(self, request: Request) -> None:
        print("on_accept_action: ", request.sid)
        await self.game_manager.accept_action(request)

    @with_request
    async def on_reveal(self, request: Request, influence: int) -> None:
        print("on_reveal: ", request.sid, influence)
        await self.game_manager.reveal_influence(request, Influence(influence))

    @with_request
    async def on_challenge(self, request: Request) -> None:
        print("on_challenge: ", request.sid)
        await self.game_manager.challenge(request)

    @with_request
    async def on_block(self, request: Request) -> None:
        print("on_block: ", request.sid)
        await self.game_manager.block(request)

    @with_request
    async def on_accept_block(self, request: Request) -> None:
        print("on_accept_block: ", request.sid)
        await self.game_manager.accept_block(request)

    @with_request
    async def on_challenge_block(self, request: Request) -> None:
        print("on_challenge_block: ", request.sid)
        await self.game_manager.challenge_block(request)

    @with_request
    async def on_exchange(self, request: Request, exchange: list[dict]) -> None:
        print("on_exchange: ", request.sid, exchange)
        await self.game_manager.exchange(
            request,
            [
                ExchangeInfluence(
                    Influence(e["influence"]),
                    e["selected"],
                )
                for e in exchange
            ],
        )
