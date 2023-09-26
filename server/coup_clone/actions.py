from typing import Awaitable, Callable, Optional

from attr import dataclass

from coup_clone.db.games import TurnAction, TurnState
from coup_clone.db.players import Influence
from coup_clone.models import Game
from coup_clone.utils import FunctionRegistry


@dataclass
class GameAction:
    effect: Callable[[Game], Awaitable[None]]
    success_message: Optional[str] = None
    attempt_message: Optional[str] = None
    influence: Optional[Influence] = None
    is_targetted: bool = False
    can_be_blocked_by: set[Influence] = set()
    cost: int = 0


def factory(
    effect: Callable[[Game], Awaitable[None]],
    influence: Optional[Influence] = None,
    is_targetted: bool = False,
    can_be_blocked_by: set[Influence] = set(),
    cost: int = 0,
) -> GameAction:
    return GameAction(
        effect=effect,
        influence=influence,
        is_targetted=is_targetted,
        can_be_blocked_by=can_be_blocked_by,
        cost=cost,
    )


action_registry = FunctionRegistry[TurnAction, GameAction, Awaitable[None]](factory)


@action_registry.register(
    TurnAction.INCOME,
    success_message = "{player} takes Income",
)
async def income(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins()
    await game.next_player_turn()


@action_registry.register(
    TurnAction.FOREIGN_AID,
    can_be_blocked_by={
        Influence.DUKE,
    },
    success_message = "{player} takes Foreign Aid",
    attempt_message = "{player} attempts to take Foreign Aid",
)
async def foreign_aid(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins(2)
    await game.next_player_turn()


@action_registry.register(
    TurnAction.TAX,
    influence=Influence.DUKE,
    success_message = "{player} takes Tax",
    attempt_message = "{player} attempts to take Tax",
)
async def tax(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins(3)
    await game.next_player_turn()


@action_registry.register(
    TurnAction.STEAL,
    influence=Influence.CAPTAIN,
    can_be_blocked_by={
        Influence.CAPTAIN,
        Influence.AMBASSADOR,
    },
    success_message = "{player} steals from {target}",
    attempt_message = "{player} attempts to steal from {target}",
)
async def steal(game: Game) -> None:
    current_player = await game.get_current_player()
    target = await game.get_target_player()
    await current_player.increment_coins(2)
    await target.decrement_coins(2)
    await game.next_player_turn()


@action_registry.register(
    TurnAction.ASSASSINATE,
    influence=Influence.ASSASSIN,
    is_targetted=True,
    can_be_blocked_by={
        Influence.CONTESSA,
    },
    cost=3,
    success_message = "{player} assassinates {target}",
    attempt_message = "{player} attempts to assassinate {target}",
)
async def assassinate(game: Game) -> None:
    await game.update(
        turn_state=TurnState.TARGET_REVEALING,
    )


@action_registry.register(
    TurnAction.COUP,
    is_targetted=True,
    cost=7,
    success_message = "{player} performas a coup against {target}",
)
async def coup(game: Game) -> None:
    await game.update(
        turn_state=TurnState.TARGET_REVEALING,
    )


@action_registry.register(
    TurnAction.EXCHANGE,
    influence=Influence.AMBASSADOR,
    success_message = "{player} picks up 2 cards to exchange",
    attempt_message = "{player} attempts to exchange",
)
async def exchange(game: Game) -> None:
    await game.update(turn_state=TurnState.EXCHANGING)


def get_action(action: TurnAction) -> GameAction:
    return action_registry.get(action)
