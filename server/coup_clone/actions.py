from typing import Any, Awaitable, Callable, Optional

from attr import dataclass

from coup_clone.db.games import TurnAction, TurnState
from coup_clone.db.players import Influence
from coup_clone.models import Game

ACTIONS = {}


@dataclass
class GameAction:
    effect: Callable[[Game], Awaitable[None]]
    influence: Optional[Influence] = None
    is_targetted: bool = False
    can_be_blocked_by: list[Influence] = []
    cost: int = 0


def action(
    action: TurnAction,
    influence: Optional[Influence] = None,
    is_targetted: bool = False,
    can_be_blocked_by: set[Influence] = [],
    cost: int = 0,
) -> Callable[[Callable[..., Any]], Any]:
    def wrapper(f: Callable[[Game], Awaitable[None]]) -> Callable[[Game], Awaitable[None]]:
        ACTIONS[action] = GameAction(
            effect=f,
            influence=influence,
            is_targetted=is_targetted,
            can_be_blocked_by=can_be_blocked_by,
            cost=cost,
        )
        return f

    return wrapper


@action(
    TurnAction.INCOME,
)
async def income(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins()
    await game.next_player_turn()


@action(
    TurnAction.FOREIGN_AID,
    can_be_blocked_by={
        Influence.DUKE,
    }
)
async def foreign_aid(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins(2)
    await game.next_player_turn()


@action(
    TurnAction.TAX,
    influence=Influence.DUKE,
)
async def tax(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins(3)
    await game.next_player_turn()


@action(
    TurnAction.STEAL,
    influence=Influence.CAPTAIN,
    can_be_blocked_by={
        Influence.CAPTAIN,
        Influence.AMBASSADOR,
    }
)
async def steal(game: Game) -> None:
    current_player = await game.get_current_player()
    target = await game.get_target_player()
    await current_player.increment_coins(2)
    await target.decrement_coins(2)
    await game.next_player_turn()


@action(
    TurnAction.ASSASSINATE,
    influence=Influence.ASSASSIN,
    is_targetted=True,
    can_be_blocked_by={
        Influence.CONTESSA,
    },
    cost=3
)
async def assassinate(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.decrement_coins(3)
    await game.update(
        turn_state=TurnState.TARGET_REVEALING,
    )


@action(
    TurnAction.EXCHANGE,
    influence=Influence.AMBASSADOR,
)
async def exchange(game: Game) -> None:
    await game.update(turn_state=TurnState.EXCHANGING)
