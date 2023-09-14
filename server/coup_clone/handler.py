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
                    *args,
                )
            except NoActiveSessionException:
                raise

    return wrapper


def log_event(f: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(f)
    async def wrapper(self: "Handler", sid: str, *args: Any) -> None:
        print(f.__name__, sid)
        await f(self, sid, *args)

    return wrapper


def socket_response(f: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(f)
    async def wrapper(self: "Handler", *args: Any) -> dict:
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
            return {"status": "error", "error": e.as_error_response()}

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

    @log_event
    async def on_connect(self, sid: str, environ: dict, auth: dict) -> None:
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

    @socket_response
    @log_event
    @with_request
    async def on_create_game(self, request: Request) -> None:
        await self.game_manager.create(request)

    @socket_response
    @log_event
    @with_request
    async def on_join_game(self, request: Request, game_id: str) -> None:
        await self.game_manager.join(request, game_id.lower())

    @socket_response
    @log_event
    @with_request
    async def on_leave_game(self, request: Request) -> None:
        await self.game_manager.leave(request)

    @socket_response
    @log_event
    @with_request
    async def on_initialize_game(self, request: Request) -> None:
        player = await request.session.get_playerX()
        await self.notifications_manager.notify_player(request.conn, player)

    @socket_response
    @log_event
    @with_request
    async def on_set_name(self, request: Request, name: str) -> None:
        await self.game_manager.set_name(request, name)

    @socket_response
    @log_event
    @with_request
    async def on_start_game(self, request: Request) -> None:
        await self.game_manager.start(request)

    @socket_response
    @log_event
    @with_request
    async def on_take_action(self, request: Request, action: dict) -> None:
        await self.game_manager.take_action(request, action["action"], action.get("target", None))

    @socket_response
    @log_event
    @with_request
    async def on_accept_action(self, request: Request) -> None:
        await self.game_manager.accept_action(request)

    @socket_response
    @log_event
    @with_request
    async def on_reveal(self, request: Request, influence: int) -> None:
        await self.game_manager.reveal_influence(request, Influence(influence))

    @socket_response
    @log_event
    @with_request
    async def on_challenge(self, request: Request) -> None:
        await self.game_manager.challenge(request)

    @socket_response
    @log_event
    @with_request
    async def on_block(self, request: Request) -> None:
        await self.game_manager.block(request)

    @socket_response
    @log_event
    @with_request
    async def on_accept_block(self, request: Request) -> None:
        await self.game_manager.accept_block(request)

    @socket_response
    @log_event
    @with_request
    async def on_challenge_block(self, request: Request) -> None:
        await self.game_manager.challenge_block(request)

    @socket_response
    @log_event
    @with_request
    async def on_exchange(self, request: Request, exchange: list[dict]) -> None:
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
