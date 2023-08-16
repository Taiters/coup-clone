import enum
from dataclasses import dataclass
from typing import Optional

from aiosqlite import Cursor, Row

from coup_clone.db.table import Table, TableRow


class TurnState(enum.IntEnum):
    START = 0
    BLOCK = 1
    CHALLENGED = 2
    BLOCK_CHALLENGED = 3
    SUCCESS = 4
    FAIL = 5


class TurnAction(enum.IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    TAX = 2
    STEAL = 3
    EXCHANGE = 4
    ASSASSINATE = 5
    COUP = 6


@dataclass
class TurnRow(TableRow[int]):
    action: TurnAction
    state: TurnState
    player_id: int
    target_id: Optional[int]
    challenged_by_id: Optional[int]
    blocked_by_id: Optional[int]
    block_challenged_by_id: Optional[int]


class TurnsTable(Table[TurnRow, int]):
    TABLE_NAME = "turns"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS turns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER REFERENCES games
                ON DELETE CASCADE
                NOT NULL,
            target_id INTEGER REFERENCES players,
            challenged_by_id INTEGER REFERENCES players,
            blocked_by_id INTEGER REFERENCES players,
            block_challenged_by_id INTEGER REFERENCES players,
            action INTEGER,
            state INTEGER NOT NULL DEFAULT(0)
        );
    """
    COLUMNS = [
        "id",
        "player_id",
        "target_id",
        "challenged_by_id",
        "blocked_by_id",
        "block_challenged_by_id",
        "action",
        "state",
    ]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> TurnRow:
        return TurnRow(
            id=row[0],
            player_id=row[1],
            target_id=row[2],
            challenged_by_id=row[3],
            blocked_by_id=row[4],
            block_challenged_by_id=row[5],
            action=TurnAction(row[6]),
            state=TurnState(row[7]),
        )
