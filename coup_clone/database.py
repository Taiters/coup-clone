import aiosqlite

from contextlib import asynccontextmanager
from aiosqlite import Connection

from coup_clone import players, games, events

DB_FILE = "./test.db"
TABLE_DEFINITIONS = [
    players.TABLE_DEFINITION,
    games.TABLE_DEFINITION,
    events.TABLE_DEFINITION,
]


@asynccontextmanager
async def open_db() -> Connection:
    async with aiosqlite.connect(DB_FILE) as db:
        yield db


async def create_tables(db: Connection) -> None:
    for table in TABLE_DEFINITIONS:
        await db.execute(table)
    await db.commit()
