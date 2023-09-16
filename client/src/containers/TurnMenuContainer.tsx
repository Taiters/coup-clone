import AttemptedTurnMenu from "../components/AttemptedTurnMenu";
import BlockedMenu from "../components/BlockedMenu";
import ExchangingTurnMenu from "../components/ExchangingTurnMenu";
import FinishedGameTurnMenu from "../components/FinishedGameTurnMenu";
import RevealingActionMenu from "../components/RevealingActionMenu";
import StartTurnMenu from "../components/StartTurnMenu";
import { Game, GameState, Player, PlayerInfluence, TurnState } from "../types";
import { nullthrows } from "../utils";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function TurnMenuContainer({ game, players, currentPlayer }: Props) {
  switch (game.state) {
    case GameState.RUNNING:
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
          return (
            <AttemptedTurnMenu
              game={game}
              players={players}
              currentPlayer={currentPlayer}
            />
          );
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
        case TurnState.EXCHANGING:
          return (
            <ExchangingTurnMenu game={game} currentPlayer={currentPlayer} />
          );
        default:
          throw new Error("Unhandled turn state for running game");
      }

    case GameState.FINISHED:
      return <FinishedGameTurnMenu game={game} currentPlayer={currentPlayer} />;

    default:
      throw new Error("Unhandled game state");
  }
}

export default TurnMenuContainer;
