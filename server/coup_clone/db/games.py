import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from aiosqlite import Cursor, Row

from coup_clone.db.table import Table, TableRow


class GameState(enum.IntEnum):
    LOBBY = 0
    RUNNING = 1
    FINISHED = 2


class TurnState(enum.IntEnum):
    START = 0
    ATTEMPTED = 1
    BLOCKED = 2
    CHALLENGED = 3
    BLOCK_CHALLENGED = 4
    REVEALING = 5
    TARGET_REVEALING = 6
    CHALLENGER_REVEALING = 7
    BLOCK_CHALLENGER_REVEALING = 8


class TurnAction(enum.IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    TAX = 2
    STEAL = 3
    EXCHANGE = 4
    ASSASSINATE = 5
    COUP = 6


@dataclass()
class GameRow(TableRow[str]):
    state: GameState
    deck: str
    player_turn_id: Optional[int]
    turn_action: Optional[TurnAction]
    turn_state: Optional[TurnState]
    target_id: Optional[int]
    challenged_by_id: Optional[int]
    blocked_by_id: Optional[int]
    block_challenged_by_id: Optional[int]
    turn_state_modified: Optional[datetime]
    turn_state_deadline: Optional[datetime]
    winner_id: Optional[int]


class GamesTable(Table[GameRow, str]):
    TABLE_NAME = "games"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            state INTEGER NOT NULL DEFAULT(0),
            deck TEXT NOT NULL,
            player_turn_id INTEGER REFERENCES players,
            turn_action INTEGER,
            turn_state INTEGER,
            target_id INTEGER REFERENCES players,
            challenged_by_id INTEGER REFERENCES players,
            blocked_by_id INTEGER REFERENCES players,
            block_challenged_by_id INTEGER REFERENCES players,
            turn_state_modified DATETIME,
            turn_state_deadline DATETIME,
            winner_id INTEGER REFERENCES players
        );
    """
    COLUMNS = [
        "id",
        "state",
        "deck",
        "player_turn_id",
        "turn_action",
        "turn_state",
        "target_id",
        "challenged_by_id",
        "blocked_by_id",
        "block_challenged_by_id",
        "turn_state_modified",
        "turn_state_deadline",
        "winner_id",
    ]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> GameRow:
        return GameRow(
            id=row[0],
            state=GameState(row[1]),
            deck=row[2],
            player_turn_id=row[3],
            turn_action=TurnAction(row[4]) if row[4] is not None else None,
            turn_state=TurnState(row[5]) if row[5] is not None else None,
            target_id=row[6],
            challenged_by_id=row[7],
            blocked_by_id=row[8],
            block_challenged_by_id=row[9],
            turn_state_modified=datetime.fromisoformat(row[10]) if row[10] is not None else None,
            turn_state_deadline=datetime.fromisoformat(row[11]) if row[11] is not None else None,
            winner_id=row[12],
        )
