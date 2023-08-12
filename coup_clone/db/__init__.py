from typing import AsyncIterator
import aiosqlite

from contextlib import asynccontextmanager
from aiosqlite import Connection

from .players import PlayersTable
from .events import EventsTable
from .games import GamesTable
from .sessions import SessionsTable


DB_FILE = "./test.db"
TABLE_DEFINITIONS = [
    PlayersTable.TABLE_DEFINITION,
    EventsTable.TABLE_DEFINITION,
    GamesTable.TABLE_DEFINITION,
    SessionsTable.TABLE_DEFINITION,
]


@asynccontextmanager
async def open() -> AsyncIterator[Connection]:
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        yield db


async def init(db: Connection) -> None:
    for table in TABLE_DEFINITIONS:
        await db.execute(table)
    await db.commit()
