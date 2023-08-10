import enum
from coup_clone.players import Influence

from aiosqlite import Connection

from datetime import datetime
from dataclasses import dataclass
from typing import Optional


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
class Event:
    id: int
    game_id: str
    parent_id: Optional[int]
    actor_id: int
    target_id: Optional[int]
    time_created: datetime
    event_type: EventType
    coins: Optional[int]
    revealed: Optional[Influence]
    success: Optional[bool]


async def create_event(
    db: Connection,
    game_id: str,
    actor_id: int,
    event_type: EventType,
    target_id=None,
    coins=None,
    revealed=None,
) -> Event:
    cursor = await db.execute('''
        INSERT INTO events (
            game_id,
            actor_id,
            event_type,
            target_id,
            coins,
            revealed
        ) VALUES(
            :game_id,
            :actor_id,
            :event_type,
            :target_id,
            :coins,
            :revealed
        );
    ''', {
        'game_id': game_id,
        'actor_id': actor_id,
        'event_type': event_type,
        'target_id': target_id,
        'coins': coins,
        'revealed': revealed,
    })
    event_id = cursor.lastrowid
    await db.commit()
    return await get_event(db, event_id)


async def get_event(db: Connection, id: int) -> Event:
    async with db.execute(
    '''
    SELECT  
        id,
        game_id,
        parent_id,
        actor_id,
        target_id,
        time_created,
        event_type,
        coins,
        revealed,
        success
    FROM events WHERE id = ?
    ''', (id,)) as cursor:
        row = await cursor.fetchone()
        print(row)
        return Event(
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
