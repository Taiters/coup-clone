from dataclasses import dataclass
import datetime
import enum
from sqlite3 import Cursor, Row
from typing import Optional
from coup_clone.db.players import Influence
from coup_clone.db.table import Table, TableRow


class EventType(enum.IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    EXCHANGE = 2
    TAX = 3
    STEAL = 4
    ASSASSINATE = 5
    COUP = 6
    BLOCK = 7
    CHALLENGE = 8
    GIVE = 9
    REVEAL = 10
    OUT = 11
    WIN = 12


@dataclass
class EventRow(TableRow[int]):
    game_id: str
    parent_id: Optional[int]
    actor_id: int
    target_id: Optional[int]
    time_created: datetime
    event_type: EventType
    coins: Optional[int]
    revealed: Optional[Influence]
    success: Optional[bool]


class EventsTable(Table[EventRow, id]):
    TABLE_NAME = 'events'
    TABLE_DEFINITION = '''
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
            target_id INTEGER REFERENCES players
                ON DELETE CASCADE,
            time_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event_type INTEGER NOT NULL,
            coins INTEGER,
            revealed INTEGER,
            success
        );
    '''
    COLUMNS = [
        'id',
        'game_id',
        'parent_id',
        'actor_id',
        'target_id',
        'time_created',
        'event_type',
        'coins',
        'revealed',
        'success',
    ]


    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> EventRow:
        return EventRow(
            id=row[0],
            game_id=row[1],
            parent_id=row[2],
            actor_id=row[3],
            target_id=row[4],
            time_created=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S'),
            event_type=EventType(row[6]),
            coins=row[7],
            revealed=row[8],
            success=row[9],
        )