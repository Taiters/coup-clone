import enum
from dataclasses import dataclass
from typing import Optional

from aiosqlite import Cursor, Row

from coup_clone.db.table import Table, TableRow


class PlayerState(enum.IntEnum):
    PENDING = 0
    READY = 1


class Influence(enum.IntEnum):
    UNKNOWN = 0
    DUKE = 1
    AMBASSADOR = 2
    ASSASSIN = 3
    CONTESSA = 4
    CAPTAIN = 5


@dataclass
class PlayerRow(TableRow[int]):
    game_id: str
    state: PlayerState
    name: Optional[str]
    coins: int
    influence_a: Influence
    influence_b: Influence
    revealed_influence_a: bool
    revealed_influence_b: bool
    host: bool
    accepts_action: bool


class PlayersTable(Table[PlayerRow, int]):
    TABLE_NAME = "players"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER REFERENCES games
                ON DELETE CASCADE
                NOT NULL,
            state INTEGER NOT NULL DEFAULT(0),
            name TEXT,
            coins INTEGER NOT NULL DEFAULT(2) CHECK (coins >= 0),
            influence_a INTEGER NOT NULL,
            influence_b INTEGER NOT NULL,
            revealed_influence_a INTEGER NOT NULL DEFAULT(0),
            revealed_influence_b INTEGER NOT NULL DEFAULT(0),
            host INTEGER NOT NULL DEFAULT(0),
            accepts_action INTEGER DEFAULT(0)
        );
    """
    COLUMNS = [
        "id",
        "game_id",
        "state",
        "name",
        "coins",
        "influence_a",
        "influence_b",
        "revealed_influence_a",
        "revealed_influence_b",
        "host",
        "accepts_action",
    ]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> PlayerRow:
        return PlayerRow(
            id=row[0],
            game_id=row[1],
            state=PlayerState(row[2]),
            name=row[3],
            coins=row[4],
            influence_a=Influence(row[5]),
            influence_b=Influence(row[6]),
            revealed_influence_a=row[7],
            revealed_influence_b=row[8],
            host=row[9],
            accepts_action=row[10],
        )

    @staticmethod
    async def reset_accepts_action(cursor: Cursor, game_id: str) -> None:
        await cursor.execute(
            """
        UPDATE players
        SET accepts_action = 0
        WHERE game_id = :game_id
        """,
            {"game_id": game_id},
        )
