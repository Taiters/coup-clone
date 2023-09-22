from coup_clone.models import Game
from server.coup_clone.managers.exceptions import NotPlayerTurnException


class StartGameState:
    def __init__(self, game: Game):
        self.game = game

    async def take_action(self, action):
        current_player = await self.game.get_current_player()
        if action.actor != current_player:
            raise NotPlayerTurnException()
        
        if issubclass(action, DeferredAction):
            await action.start(self.game)
        else:
            await action.execute(self.game)