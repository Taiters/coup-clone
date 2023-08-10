import random
import string
import enum

from dataclasses import dataclass
from aiosqlite import Connection


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


async def create_game(db: Connection) -> Game:
    game_id = "".join([
        random.choice(string.ascii_lowercase) 
        for _ in range(6)
    ])
    deck = ''.join(random.sample(DECK, k=len(DECK)))
    await db.execute('INSERT INTO games (id, deck) VALUES(:game_id, :deck)', {
        'game_id': game_id,
        'deck': deck
    })
    await db.commit()
    return await get_game(db, game_id)


async def get_game(db: Connection, id: str) -> Game:
    async with db.execute('SELECT id, state, deck FROM games WHERE id = ?', (id,)) as cursor:
        row = await cursor.fetchone()
        return Game(
            id=row[0],
            state=GameState(row[1]),
            deck=row[2],
        )
