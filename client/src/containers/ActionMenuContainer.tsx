import AttemptedActionMenu from "../components/AttemptedActionMenu";
import BlockedMenu from "../components/BlockedMenu";
import CurrentTurn from "../components/CurrentTurn";
import RevealingActionMenu from "../components/RevealingActionMenu";
import WaitingForPlayer from "../components/WaitingForPlayer";
import { Game, Player, PlayerInfluence, TurnState } from "../types";
import { nullthrows } from "../utils";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function ActionMenuContainer({ game, players, currentPlayer }: Props) {
  if (
    currentPlayer.influenceA !== PlayerInfluence.UNKNOWN &&
    currentPlayer.influenceB !== PlayerInfluence.UNKNOWN
  ) {
    return <p>You are out</p>;
  }

  switch (game.turnState) {
    case TurnState.START:
      return currentPlayer.isCurrentTurn ? (
        <CurrentTurn currentPlayer={currentPlayer} players={players} />
      ) : (
        <WaitingForPlayer player={game.currentTurn} />
      );
    case TurnState.ATTEMPTED:
      return <AttemptedActionMenu game={game} currentPlayer={currentPlayer} />;
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
          <p>
            {game.turnChallenger?.name ?? "UNKOWN"} has challenged{" "}
            {game.currentTurn.name}!
          </p>
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

export default ActionMenuContainer;
