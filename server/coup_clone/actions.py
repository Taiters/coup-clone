from abc import ABC, abstractmethod

from aiosqlite import Cursor

from coup_clone.db.games import TurnAction
from coup_clone.managers.exceptions import (
    NotPlayerTurnException,
    PlayerNotInGameException,
)
from coup_clone.models import Game, Player
from coup_clone.request import Request

TURN_WAIT_SECONDS = 10


class Action(ABC):
    def __init__(self, request: Request):
        self.request = request

    async def execute(self, cursor: Cursor) -> bool:
        current_player = await self.request.session.get_player()
        if current_player is None:
            raise PlayerNotInGameException()

        game = await current_player.get_game()
        if game.row.player_turn_id != current_player.id:
            raise NotPlayerTurnException()

        # if game.turn_state != TurnState.START:
        #     raise InvalidActionException()

        return await self.executeImpl(cursor, current_player, game)

    @abstractmethod
    async def executeImpl(self, cursor: Cursor, current_player: Player, current_game: Game) -> bool:
        ...


class Income(Action):
    async def executeImpl(self, cursor: Cursor, current_player: Player, _: Game) -> bool:
        await current_player.increment_coins()
        return True


class ForeignAid(Action):
    async def executeImpl(self, cursor: Cursor, current_player: Player, game: Game) -> bool:
        await game.set_action_deadline(TurnAction.FOREIGN_AID)
        return False


class Tax(Action):
    async def executeImpl(self, cursor: Cursor, current_player: Player, game: Game) -> bool:
        await game.set_action_deadline(TurnAction.TAX)
        return False
