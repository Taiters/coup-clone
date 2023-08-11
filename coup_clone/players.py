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
        influence_a INTEGER,
        influence_b INTEGER,
        revealed_influence_a INTEGER NOT NULL DEFAULT(0),
        revealed_influence_b INTEGER NOT NULL DEFAULT(0),
        host INTEGER NOT NULL DEFAULT(0)
    );
'''


COLUMNS = '''
    players.id,
    players.game_id,
    players.state,
    players.name,
    players.coins,
    players.influence_a,
    players.influence_b,
    players.revealed_influence_a,
    players.revealed_influence_b,
    players.host
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
    influence_a: Optional[Influence]
    influence_b: Optional[Influence]
    revealed_influence_a: bool
    revealed_influence_b: bool
    host: bool


def _player_from_row(row) -> Player:
    return Player(
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


async def create_player(db: Connection, game_id: str, host: bool=False) -> int:
    async with await db.execute('INSERT INTO players (game_id, host) VALUES(:game_id, :host)', {
        'game_id': game_id,
        'host': host,
    }) as cursor:
        await cursor.execute('SELECT id FROM players WHERE ROWID = :rowid', {'rowid': cursor.lastrowid})
        row = await cursor.fetchone()
        return row[0]


async def get_player(db: Connection, id: int) -> Optional[Player]:
    async with db.execute((
        f'SELECT {COLUMNS} '
        'FROM players WHERE id = :id'
    ), {
        'id': id,
    }) as cursor:
        row = await cursor.fetchone()
        if row is None:
            return None
        return _player_from_row(row)


async def set_name(db: Connection, id: int, name: str) -> None:
    await db.execute('UPDATE players SET name = :name, state = :state WHERE id = :id', {
        'name': name,
        'state': PlayerState.READY,
        'id': id,
    })


async def get_players_in_game(db: Connection, game_id: int) -> List[Player]:
    async with db.execute((
        f'SELECT {COLUMNS} '
        'FROM players WHERE players.game_id = :game_id ORDER BY players.id'
    ), {
        'game_id': game_id,
    }) as cursor:
        rows = await cursor.fetchall()
        return [_player_from_row(row) for row in rows]


async def get_player_from_session(db: Connection, session_id: int) -> Optional[Player]:
    async with await db.execute((
        f'SELECT {COLUMNS} '
        'FROM players JOIN sessions ON players.id = sessions.player_id '
        'WHERE sessions.id = :session_id'
    ), {
        'session_id': session_id,
    }) as cursor:
        row = await cursor.fetchone()
        if row is None:
            return None
        return _player_from_row(row)


async def delete_player(db: Connection, id: int) -> None:
    await db.execute('DELETE FROM players WHERE players.id = :id', {'id': id})
