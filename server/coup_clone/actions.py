import enum
from abc import ABC, abstractmethod

from aiosqlite import Cursor

from coup_clone.db.games import GamesTable
from server.coup_clone.db.players import PlayersTable


class ActionType(enum.IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    TAX = 2
    STEAL = 3
    ASSASSINATE = 4
    EXCHANGE = 5
    COUP = 6


class Action(ABC):
    def __init__(
        self, cursor: Cursor, games_table: GamesTable, players_table: PlayersTable, type: ActionType, player_id: int
    ):
        self.cursor = cursor
        self.games_table = games_table
        self.players_table = players_table
        self.action_type = type
        self.player_id = player_id

    @abstractmethod
    async def execute(self):
        ...

    async def get_player(self):
        return await self.players_table.get(self.cursor, self.player_id)


class TargetedAction(Action):
    def __init__(
        self,
        cursor: Cursor,
        games_table: GamesTable,
        players_table: PlayersTable,
        type: ActionType,
        player_id: int,
        target_id: int,
    ):
        self.target_id = target_id
        super().__init__(cursor, games_table, players_table, type, player_id)


class Income(Action):
    async def execute(self):
        player = await self.get_player()
        await self.players_table.update(self.cursor, self.player_id, coins=player.coins + 1)

