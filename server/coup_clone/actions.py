from abc import ABC, abstractmethod
from coup_clone.models import Game, Player

class GameAction(ABC):
    def __init__(self, actor: Player):
        self.actor = actor
    
    @abstractmethod
    async def execute(self, game: Game) -> None:
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

class Tax(GameAction):
    async def execute(self):
        current_player = await self.game.get_current_player()
        await current_player.increment_coins(3)
        await self.game.next_player_turn()