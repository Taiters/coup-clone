from abc import ABC, abstractmethod

from aiosqlite import Cursor

from coup_clone.db.games import GameRow, GamesTable
from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.managers.exceptions import (
    NotPlayerTurnException,
    PlayerNotInGameException,
)
from coup_clone.session import ActiveSession


class Action(ABC):
    def __init__(self, session: ActiveSession, games_table: GamesTable, players_table: PlayersTable):
        self.session = session
        self.games_table = games_table
        self.players_table = players_table

    async def execute(self, cursor: Cursor) -> None:
        current_player = await self.session.current_player(cursor)
        if current_player is None:
            raise PlayerNotInGameException()

        game = await self.games_table.get(cursor, current_player.game_id)
        if game.player_turn_id != current_player.id:
            raise NotPlayerTurnException()

        await self.executeImpl(cursor, current_player, game)

    @abstractmethod
    async def executeImpl(self, cursor: Cursor, current_player: PlayerRow, current_game: GameRow) -> None:
        ...

    @abstractmethod
    def log_message(self) -> str:
        ...


class Income(Action):
    async def executeImpl(self, cursor: Cursor, current_player: PlayerRow, _: GameRow) -> None:
        await self.players_table.increment_coins(cursor, current_player.id)

    def log_message(self) -> str:
        return f"@<player:{self.session.player_id}> took INCOME and received 1 coin"
