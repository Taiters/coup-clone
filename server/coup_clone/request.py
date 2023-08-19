import functools
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar
from aiosqlite import Connection
from attr import dataclass

from coup_clone.models import Session
from coup_clone import db
from coup_clone.managers.exceptions import NoActiveSessionException
from coup_clone.handler import Handler


@dataclass
class Request:
    sid: str
    conn: Connection
    session: Session

T = TypeVar('T')
P = ParamSpec('P')

async def with_request(f: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(f)
    async def wrapper(self: Handler, sid: str, *args: Any) -> None:
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
                await self.disconnect(sid)
                raise
    return wrapper
