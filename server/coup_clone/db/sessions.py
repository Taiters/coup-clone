from dataclasses import dataclass
from typing import Optional

from aiosqlite import Cursor, Row

from coup_clone.db.table import Table, TableRow


@dataclass
class SessionRow(TableRow[str]):
    player_id: Optional[int]


class SessionsTable(Table[SessionRow, str]):
    TABLE_NAME = "sessions"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            player_id INTEGER REFERENCES players
                ON DELETE SET NULL
        );
    """
    COLUMNS = [
        "id",
        "player_id",
    ]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> SessionRow:
        return SessionRow(
            id=row[0],
            player_id=row[1],
        )
