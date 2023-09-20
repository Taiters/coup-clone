from abc import ABC, abstractmethod
from coup_clone.models import Game
from coup_clone.db.players import Influence
from coup_clone.db.games import TurnAction

class GameAction(ABC):
    def __init__(self, game: Game):
        self.game = game
    
    @staticmethod
    def can_be_challenged() -> bool:
        return False

    @staticmethod
    def can_be_blocked() -> bool:
        return False
    
    @abstractmethod
    async def execute(self) -> None:
        ...


class Income(GameAction):
    async def execute(self):
        current_player = await self.game.get_current_player()
        await current_player.increment_coins()
        await self.game.next_player_turn()

class Tax(GameAction):
    async def execute(self):
        current_player = await self.game.get_current_player()
        await current_player.increment_coins(3)
        await self.game.next_player_turn()