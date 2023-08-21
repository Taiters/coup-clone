from aiosqlite import Connection
from attr import dataclass

from coup_clone.models import Session


@dataclass
class Request:
    sid: str
    conn: Connection
    session: Session
