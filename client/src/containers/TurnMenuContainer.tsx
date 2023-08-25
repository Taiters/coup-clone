import AttemptedTurnMenu from "../components/AttemptedTurnMenu";
import BlockedMenu from "../components/BlockedMenu";
import RevealingActionMenu from "../components/RevealingActionMenu";
import StartTurnMenu from "../components/StartTurnMenu";
import { Game, Player, PlayerInfluence, TurnState } from "../types";
import { nullthrows } from "../utils";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function TurnMenuContainer({ game, players, currentPlayer }: Props) {
  if (
    currentPlayer.influenceA !== PlayerInfluence.UNKNOWN &&
    currentPlayer.influenceB !== PlayerInfluence.UNKNOWN
  ) {
    return <p>You are out</p>;
  }

  switch (game.turnState) {
    case TurnState.START:
      return (
        <StartTurnMenu
          game={game}
          players={players}
          currentPlayer={currentPlayer}
        />
      );
    case TurnState.ATTEMPTED:
      return <AttemptedTurnMenu game={game} currentPlayer={currentPlayer} />;
    case TurnState.TARGET_REVEALING:
      return (
        <RevealingActionMenu
          playerToReveal={nullthrows(game.turnTarget)}
          currentPlayer={currentPlayer}
        />
      );
    case TurnState.REVEALING:
      return (
        <RevealingActionMenu
          playerToReveal={nullthrows(game.currentTurn)}
          currentPlayer={currentPlayer}
        />
      );
    case TurnState.CHALLENGER_REVEALING:
      return (
        <RevealingActionMenu
          playerToReveal={nullthrows(game.turnChallenger)}
          currentPlayer={currentPlayer}
        />
      );
    case TurnState.CHALLENGED:
      return (
        <>
          <RevealingActionMenu
            playerToReveal={nullthrows(game.currentTurn)}
            currentPlayer={currentPlayer}
          />
        </>
      );
    case TurnState.BLOCKED:
      return <BlockedMenu game={game} currentPlayer={currentPlayer} />;
    case TurnState.BLOCK_CHALLENGED:
      return (
        <RevealingActionMenu
          playerToReveal={nullthrows(game.turnBlocker)}
          currentPlayer={currentPlayer}
        />
      );
    case TurnState.BLOCK_CHALLENGER_REVEALING:
      return (
        <RevealingActionMenu
          playerToReveal={nullthrows(game.turnBlockChallenger)}
          currentPlayer={currentPlayer}
        />
      );
    default:
      return <p>Hmm...</p>;
  }
}

export default TurnMenuContainer;
