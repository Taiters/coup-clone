from abc import ABC, abstractmethod

from aiosqlite import Cursor

from coup_clone.db.games import GameRow, GamesTable, TurnAction, TurnState
from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.managers.exceptions import (
    InvalidActionException,
    NotPlayerTurnException,
    PlayerNotInGameException,
)
from coup_clone.session import ActiveSession

TURN_WAIT_SECONDS = 10


class Action(ABC):
    def __init__(self, session: ActiveSession, games_table: GamesTable, players_table: PlayersTable):
        self.session = session
        self.games_table = games_table
        self.players_table = players_table

    async def execute(self, cursor: Cursor) -> bool:
        current_player = await self.session.current_player(cursor)
        if current_player is None:
            raise PlayerNotInGameException()

        game = await self.games_table.get(cursor, current_player.game_id)
        if game.player_turn_id != current_player.id:
            raise NotPlayerTurnException()

        # if game.turn_state != TurnState.START:
        #     raise InvalidActionException()

        return await self.executeImpl(cursor, current_player, game)

    @abstractmethod
    async def executeImpl(self, cursor: Cursor, current_player: PlayerRow, current_game: GameRow) -> bool:
        ...


class Income(Action):
    async def executeImpl(self, cursor: Cursor, current_player: PlayerRow, _: GameRow) -> bool:
        await self.players_table.increment_coins(cursor, current_player.id)
        return True


class ForeignAid(Action):
    async def executeImpl(self, cursor: Cursor, current_player: PlayerRow, _: GameRow) -> bool:
        await self.games_table.set_action_deadline(cursor, current_player.game_id, TurnAction.FOREIGN_AID)
        return False


class Tax(Action):
    async def executeImpl(self, cursor: Cursor, current_player: PlayerRow, _: GameRow) -> bool:
        await self.games_table.set_action_deadline(cursor, current_player.game_id, TurnAction.TAX)
        return False
