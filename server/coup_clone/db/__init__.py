from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite
from aiosqlite import Connection

from .events import EventsTable
from .games import GamesTable
from .players import PlayersTable
from .sessions import SessionsTable

DB_FILE = "./test.db"
TABLE_DEFINITIONS = [
    PlayersTable.TABLE_DEFINITION,
    EventsTable.TABLE_DEFINITION,
    GamesTable.TABLE_DEFINITION,
    SessionsTable.TABLE_DEFINITION,
]

TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS check_player_count_in_game
    BEFORE INSERT
    ON players
    WHEN (SELECT COUNT(id) FROM players WHERE game_id = NEW.game_id) >= 6
    BEGIN
        SELECT RAISE(FAIL, "Game full");
    END;
    """,
]


@asynccontextmanager
async def open() -> AsyncIterator[Connection]:
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db


async def init(db: Connection) -> None:
    for table in TABLE_DEFINITIONS:
        await db.execute(table)
    for trigger in TRIGGERS:
        await db.execute(trigger)
    await db.commit()
