from typing import Any, Awaitable, Callable, Optional

from attr import dataclass

from coup_clone.db.games import TurnAction
from coup_clone.db.players import Influence
from coup_clone.models import Game

ACTIONS = {}


@dataclass
class GameAction:
    effect: Callable[[Game], Awaitable[None]]
    requires_influence: Optional[Influence] = None
    is_targetted: bool = False
    can_challenge: bool = False
    can_be_blocked_by: list[Influence] = []
    cost: int = 0


def game_action(
    action: TurnAction,
    requires_influence: Optional[Influence] = None,
    is_targetted: bool = False,
    can_challenge: bool = False,
    can_be_blocked_by: set[Influence] = [],
) -> Callable[[Callable[..., Any]], Any]:
    def wrapper(f: Callable[[Game], Awaitable[None]]) -> Callable[[Game], Awaitable[None]]:
        ACTIONS[action] = GameAction(
            effect=f,
            requires_influence=requires_influence,
            is_targetted=is_targetted,
            can_challenge=can_challenge,
            can_be_blocked_by=can_be_blocked_by,
        )
        return f

    return wrapper


@game_action(
    TurnAction.INCOME,
)
async def income(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins()
    await game.next_player_turn()


@game_action(
    TurnAction.TAX,
    requires_influence=Influence.DUKE,
    can_challenge=True,
)
async def tax(game: Game) -> None:
    current_player = await game.get_current_player()
    await current_player.increment_coins(3)
    await game.next_player_turn()


@game_action(
    TurnAction.STEAL,
    requires_influence=Influence.CAPTAIN,
    can_challenge=True,
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
