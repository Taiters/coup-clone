from dataclasses import dataclass
import enum
from aiosqlite import Cursor, Row
from typing import Optional
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
    influence_a: Optional[Influence]
    influence_b: Optional[Influence]
    revealed_influence_a: bool
    revealed_influence_b: bool
    host: bool


class PlayersTable(Table[PlayerRow, int]):
    TABLE_NAME = 'players'
    TABLE_DEFINITION = '''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER REFERENCES games 
                ON DELETE CASCADE
                NOT NULL,
            state INTEGER NOT NULL DEFAULT(0),
            name TEXT,
            coins INTEGER NOT NULL DEFAULT(3),
            influence_a INTEGER,
            influence_b INTEGER,
            revealed_influence_a INTEGER NOT NULL DEFAULT(0),
            revealed_influence_b INTEGER NOT NULL DEFAULT(0),
            host INTEGER NOT NULL DEFAULT(0)
        );
    '''
    COLUMNS = [
        'id',
        'game_id',
        'state',
        'name',
        'coins',
        'influence_a',
        'influence_b',
        'revealed_influence_a',
        'revealed_influence_b',
        'host',
    ]


    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> PlayerRow:
        return PlayerRow(
            id=row[0],
            game_id=row[1],
            state=PlayerState(row[2]),
            name=row[3],
            coins=row[4],
            influence_a=Influence(row[5]) if row[5] is not None else None,
            influence_b=Influence(row[6]) if row[6] is not None else None,
            revealed_influence_a=row[7],
            revealed_influence_b=row[8],
            host=row[9],
        )