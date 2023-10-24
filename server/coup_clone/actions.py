from typing import Awaitable, Callable, Optional

from attr import dataclass

from coup_clone.db.games import TurnAction, TurnState
from coup_clone.db.players import Influence
from coup_clone.models import Game
from coup_clone.utils import not_null


@dataclass
class GameAction:
    next_state: TurnState
    success_message: str
    effect: Optional[Callable[[Game], Awaitable[None]]] = None
    attempt_message: Optional[str] = None
    influence: Optional[Influence] = None
    is_targetted: bool = False
    can_be_blocked_by: set[Influence] = set()
    cost: int = 0


async def income(game: Game) -> None:
    current_player = not_null(await game.get_current_player())
    await current_player.increment_coins()


async def foreign_aid(game: Game) -> None:
    current_player = not_null(await game.get_current_player())
    await current_player.increment_coins(2)


async def tax(game: Game) -> None:
    current_player = not_null(await game.get_current_player())
    await current_player.increment_coins(3)


async def steal(game: Game) -> None:
    current_player = not_null(await game.get_current_player())
    target = not_null(await game.get_target_player())
    await current_player.increment_coins(2)
    await target.decrement_coins(2)


ACTIONS = {
    TurnAction.INCOME: GameAction(
        effect=income,
        next_state=TurnState.START,
        success_message="{player} takes Income",
    ),
    TurnAction.FOREIGN_AID: GameAction(
        effect=foreign_aid,
        next_state=TurnState.START,
        can_be_blocked_by={
            Influence.DUKE,
        },
        success_message="{player} takes Foreign Aid",
        attempt_message="{player} attempts to take Foreign Aid",
    ),
    TurnAction.TAX: GameAction(
        effect=tax,
        next_state=TurnState.START,
        influence=Influence.DUKE,
        success_message="{player} takes Tax",
        attempt_message="{player} attempts to take Tax",
    ),
    TurnAction.STEAL: GameAction(
        effect=steal,
        next_state=TurnState.START,
        influence=Influence.CAPTAIN,
        can_be_blocked_by={
            Influence.CAPTAIN,
            Influence.AMBASSADOR,
        },
        success_message="{player} steals from {target}",
        attempt_message="{player} attempts to steal from {target}",
    ),
    TurnAction.ASSASSINATE: GameAction(
        influence=Influence.ASSASSIN,
        next_state=TurnState.TARGET_REVEALING,
        is_targetted=True,
        can_be_blocked_by={
            Influence.CONTESSA,
        },
        cost=3,
        success_message="{player} assassinates {target}",
        attempt_message="{player} attempts to assassinate {target}",
    ),
    TurnAction.COUP: GameAction(
        next_state=TurnState.TARGET_REVEALING,
        is_targetted=True,
        cost=7,
        success_message="{player} performas a coup against {target}",
    ),
    TurnAction.EXCHANGE: GameAction(
        next_state=TurnState.EXCHANGING,
        influence=Influence.AMBASSADOR,
        success_message="{player} picks up 2 cards to exchange",
        attempt_message="{player} attempts to exchange",
    ),
}


def get_action(action: TurnAction) -> GameAction:
    result = ACTIONS[action]
    if result is None:
        raise Exception("Action not found " + str(action))
    return result
