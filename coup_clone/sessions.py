from aiosqlite import Connection
from dataclasses import dataclass


TABLE_DEFINITION = '''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        player_id INTEGER REFERENCES players
            ON DELETE SET NULL
    );
'''


async def create_session(db: Connection, id: str) -> None:
    await db.execute('INSERT INTO sessions (id) VALUES (:id);', {
        'id': id,
    })
    await db.commit()


async def set_player(db: Connection, id: str, player_id: int) -> None:
    await db.execute('UPDATE sessions SET player_id = :player_id WHERE id = :id;', {
        'id': id,
        'player_id': player_id
    })
    await db.commit()