import enum
from dataclasses import dataclass

from aiosqlite import Cursor, Row

from coup_clone.db.table import Table, TableRow


class GameState(enum.IntEnum):
    LOBBY = 0
    RUNNING = 1


@dataclass()
class GameRow(TableRow[str]):
    state: GameState
    deck: str
    current_player_turn: int


class GamesTable(Table[GameRow, str]):
    TABLE_NAME = "games"
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            state INTEGER NOT NULL DEFAULT(0),
            deck TEXT NOT NULL,
            current_player_turn INTEGER REFERENCES players
                ON DELETE RESTRICT
        );
    """
    COLUMNS = [
        "id",
        "state",
        "deck",
        "current_player_turn",
    ]

    @staticmethod
    def row_factory(cursor: Cursor, row: Row) -> GameRow:
        return GameRow(
            id=row[0],
            state=GameState(row[1]),
            deck=row[2],
            current_player_turn=row[3],
        )
