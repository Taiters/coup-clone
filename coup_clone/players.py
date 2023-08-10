from aiosqlite import Connection
import enum
from dataclasses import dataclass
from typing import Optional, List


TABLE_DEFINITION = '''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER REFERENCES games 
            ON DELETE CASCADE
            NOT NULL,
        state INTEGER NOT NULL DEFAULT(0),
        name TEXT,
        coins INTEGER NOT NULL DEFAULT(3),
        session_id TEXT NOT NULL,
        influence_a INTEGER,
        influence_b INTEGER,
        revealed_influence_a INTEGER NOT NULL DEFAULT(0),
        revealed_influence_b INTEGER NOT NULL DEFAULT(0),

        UNIQUE (game_id, session_id)
    );
'''


SELECT = '''
    SELECT  
        id,
        game_id,
        state,
        name,
        coins,
        session_id,
        influence_a,
        influence_b,
        revealed_influence_a,
        revealed_influence_b
'''


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
class Player:
    id: int
    game_id: str
    state: PlayerState
    name: Optional[str]
    coins: int
    session_id: str
    influence_a: Optional[Influence]
    influence_b: Optional[Influence]
    revealed_influence_a: bool
    revealed_influence_b: bool


def _player_from_row(row) -> Player:
    return Player(
        id=row[0],
        game_id=row[1],
        state=PlayerState(row[2]),
        name=row[3],
        coins=row[4],
        session_id=row[5],
        influence_a=Influence(row[6]) if row[6] is not None else None,
        influence_b=Influence(row[7]) if row[6] is not None else None,
        revealed_influence_a=row[8],
        revealed_influence_b=row[9],
    )


async def create_player(db: Connection, game_id: str, session_id: str) -> Player:
    cursor = await db.execute('INSERT INTO players (game_id, session_id) VALUES(:game_id, :session_id)', {
        'game_id': game_id,
        'session_id': session_id,
    })
    player_id = cursor.lastrowid
    await db.commit()
    return await get_player(db, player_id)


async def get_player(db: Connection, id: int) -> Player:
    async with db.execute((
        f'{SELECT} '
        'FROM players WHERE id = ?'
    ), (id,)) as cursor:
        row = await cursor.fetchone()
        return _player_from_row(row)


async def set_name(db: Connection, session_id: str, name: str) -> Player:
    await db.execute('UPDATE players SET name = :name, state = :state WHERE session_id = :session_id', {
        'name': name,
        'state': PlayerState.READY,
        'session_id': session_id,
    })
    player_id = cursor.lastrowid
    await db.commit()
    return await get_player(db, player_id)


async def get_players_in_game(db: Connection, game_id: int) -> List[Player]:
    async with db.execute((
        f'{SELECT} '
        'FROM players WHERE game_id = ?'
    ), (game_id,)) as cursor:
        rows = await cursor.fetchall()
        return [_player_from_row(row) for row in rows]
