import random
import string
import enum

from dataclasses import dataclass
from aiosqlite import Connection
from typing import Optional


DECK = "aaammmcccdddppp"
TABLE_DEFINITION = '''
    CREATE TABLE IF NOT EXISTS games (
        id TEXT PRIMARY KEY,
        state INTEGER NOT NULL DEFAULT(0),
        deck TEXT NOT NULL
    );
'''


class GameState(enum.IntEnum):
    LOBBY = 0
    RUNNING = 1


@dataclass
class Game:
    id: str
    state: GameState
    deck: str


async def create_game(db: Connection) -> str:
    game_id = "".join([
        random.choice(string.ascii_lowercase) 
        for _ in range(6)
    ])
    deck = ''.join(random.sample(DECK, k=len(DECK)))
    await db.execute('INSERT INTO games (id, deck) VALUES(:game_id, :deck)', {
        'game_id': game_id,
        'deck': deck
    })
    return game_id


async def get_game(db: Connection, id: str) -> Optional[Game]:
    async with db.execute('SELECT id, state, deck FROM games WHERE id = :id', {'id': id}) as cursor:
        row = await cursor.fetchone()
        if row is None:
            return None
        return Game(
            id=row[0],
            state=GameState(row[1]),
            deck=row[2],
        )


async def delete_game(db: Connection, id: str) -> None:
    await db.execute('DELETE FROM games WHERE games.id = :id', {'id': id})


async def set_state(db: Connection, id: str, state: GameState) -> None:
    await db.execute('UPDATE games SET state = :state WHERE id = :id', {
        'state': state,
        'id': id,
    })
