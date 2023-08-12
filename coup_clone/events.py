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
    parent_id=None,
) -> id:
    async with await db.execute('''
        INSERT INTO events (
            game_id,
            actor_id,
            event_type,
            target_id,
            coins,
            revealed,
            parent_id
        ) VALUES(
            :game_id,
            :actor_id,
            :event_type,
            :target_id,
            :coins,
            :revealed,
            :parent_id
        );
    ''', {
        'game_id': game_id,
        'actor_id': actor_id,
        'event_type': event_type,
        'target_id': target_id,
        'coins': coins,
        'revealed': revealed,
        'parent_id': parent_id,
    }) as cursor:
        await cursor.execute('SELECT id FROM events WHERE ROWID = :rowid', {'rowid': cursor.lastrowid})
        row = await cursor.fetchone()
        return row[0]


async def get_events_for_game(db: Connection, game_id: int) -> Event:
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
    FROM events WHERE game_id = :game_id
    ORDER BY time_created;
    ''', {'game_id': game_id}) as cursor:
        rows = await cursor.fetchall()
        return [
            Event(
                id=r[0],
                game_id=r[1],
                parent_id=r[2],
                actor_id=r[3],
                target_id=r[4],
                time_created=datetime.strptime(r[5], '%Y-%m-%d %H:%M:%S'),
                event_type=EventType(r[6]),
                coins=r[7],
                revealed=r[8],
                success=r[9],
            )
            for r in rows
        ]
