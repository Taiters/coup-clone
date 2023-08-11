from uuid import uuid4
from aiosqlite import Connection
from dataclasses import dataclass
from typing import Optional

from coup_clone import players
from coup_clone.players import Player


TABLE_DEFINITION = '''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        player_id INTEGER REFERENCES players
            ON DELETE SET NULL
    );
'''


async def create_session(db: Connection) -> str:
    id = str(uuid4())
    await db.execute('INSERT INTO sessions (id) VALUES (:id);', {
        'id': id,
    })
    return id


async def set_player(db: Connection, id: str, player_id: int) -> None:
    await db.execute('UPDATE sessions SET player_id = :player_id WHERE id = :id;', {
        'id': id,
        'player_id': player_id
    })
