from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from aiosqlite import Cursor, Row

from coup_clone.db.table import Table, TableRow


@dataclass
class EventRow(TableRow[int]):
    game_id: str
    parent_id: Optional[int]
    actor_id: int
    time_created: datetime
    message: str


class EventsTable(Table[EventRow, int]):
    TABLE_NAME = "events"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER REFERENCES games
                ON DELETE CASCADE
                NOT NULL,
            parent_id INTEGER REFERENCES events
                ON DELETE CASCADE,
            actor_id INTEGER REFERENCES players
                ON DELETE CASCADE
                NOT NULL,
            time_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message TEXT NOT NULL
        );
    """
    COLUMNS = ["id", "game_id", "parent_id", "actor_id", "time_created", "message"]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> EventRow:
        return EventRow(
            id=row[0],
            game_id=row[1],
            parent_id=row[2],
            actor_id=row[3],
            time_created=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S"),
            message=row[5],
        )
