import enum
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from aiosqlite import Cursor, Row

from coup_clone.db.players import Influence
from coup_clone.db.table import Table, TableRow
from coup_clone.managers.exceptions import GameNotFoundException


class GameState(enum.IntEnum):
    LOBBY = 0
    RUNNING = 1


class TurnState(enum.IntEnum):
    START = 0
    ATTEMPTED = 1
    BLOCKED = 2
    CHALLENGED = 3
    BLOCK_CHALLENGED = 4


class TurnAction(enum.IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    TAX = 2
    STEAL = 3
    EXCHANGE = 4
    ASSASSINATE = 5
    COUP = 6


@dataclass()
class GameRow(TableRow[str]):
    state: GameState
    deck: str
    player_turn_id: Optional[int]
    turn_action: Optional[TurnAction]
    turn_state: Optional[TurnState]
    target_id: Optional[int]
    challenged_by_id: Optional[int]
    blocked_by_id: Optional[int]
    block_challenged_by_id: Optional[int]
    turn_state_deadline: Optional[datetime]


class GamesTable(Table[GameRow, str]):
    TABLE_NAME = "games"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            state INTEGER NOT NULL DEFAULT(0),
            deck TEXT NOT NULL,
            player_turn_id INTEGER REFERENCES players,
            turn_action INTEGER,
            turn_state INTEGER,
            target_id INTEGER REFERENCES players,
            challenged_by_id INTEGER REFERENCES players,
            blocked_by_id INTEGER REFERENCES players,
            block_challenged_by_id INTEGER REFERENCES players,
            turn_state_deadline DATETIME
        );
    """
    COLUMNS = [
        "id",
        "state",
        "deck",
        "player_turn_id",
        "turn_action",
        "turn_state",
        "target_id",
        "challenged_by_id",
        "blocked_by_id",
        "block_challenged_by_id",
        "turn_state_deadline",
    ]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> GameRow:
        return GameRow(
            id=row[0],
            state=GameState(row[1]),
            deck=row[2],
            player_turn_id=row[3],
            turn_action=TurnAction(row[4]) if row[4] is not None else None,
            turn_state=TurnState(row[5]) if row[5] is not None else None,
            target_id=row[6],
            challenged_by_id=row[7],
            blocked_by_id=row[8],
            block_challenged_by_id=row[9],
            turn_state_deadline=datetime.strptime(row[10], "%Y-%m-%d %H:%M:%S") if row[10] is not None else None,
        )

    async def reset_turn_state(self, cursor: Cursor, game_id: str, player_id: int) -> None:
        await self.update(
            cursor,
            game_id,
            player_turn_id=player_id,
            turn_state=TurnState.START,
            turn_action=None,
            target_id=None,
            challenged_by_id=None,
            blocked_by_id=None,
            block_challenged_by_id=None,
            turn_state_deadline=None,
        )

    async def take_from_deck(self, cursor: Cursor, game_id: str, n: int = 2) -> list[Influence]:
        game = await self.get(cursor, game_id)
        if game is None:
            raise GameNotFoundException()
        deck = list(game.deck)
        popped = [Influence(int(deck.pop())) for i in range(n)]
        await self.update(cursor, game.id, deck="".join(deck))
        return popped

    async def return_to_deck(self, cursor: Cursor, game_id: str, influence: list[Influence]) -> None:
        game = await self.get(cursor, game_id)
        if game is None:
            raise GameNotFoundException()
        deck = list(game.deck) + [i.value for i in influence]
        random.shuffle(deck)
        await self.update(cursor, game.id, deck="".join(str(c) for c in deck))

    async def set_action_deadline(
        self, cursor: Cursor, game_id: str, action: TurnAction, seconds_from_now: int = 10
    ) -> None:
        await cursor.execute(
            """
            UPDATE games
            SET
                turn_state_deadline = DATETIME('now', :seconds_from_now),
                turn_action = :action,
                turn_state = :state
            WHERE id = :id
            """,
            {
                "id": game_id,
                "action": action,
                "seconds_from_now": f"+{seconds_from_now} seconds",
                "state": TurnState.ATTEMPTED,
            },
        )
