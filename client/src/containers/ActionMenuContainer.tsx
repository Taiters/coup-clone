import CurrentTurn from "../components/CurrentTurn";
import WaitingForPlayer from "../components/WaitingForPlayer";
import Button from "../components/ui/Button";
import { socket } from "../socket";
import { Game, Player, TurnAction, TurnState } from "../types";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function ActionMenuContainer({ game, players, currentPlayer }: Props) {
  switch (game.turnState) {
    case TurnState.START:
      return currentPlayer.isCurrentTurn ? (
        <CurrentTurn currentPlayer={currentPlayer} players={players} />
      ) : (
        <WaitingForPlayer player={game.currentTurn} />
      );
    case TurnState.ATTEMPTED:
      return (
        <>
          <p>
            {game.currentTurn.name} has attempted {TurnAction[game.turnAction]}
          </p>
          <Button label="accept" onClick={() => socket.emit("accept_action")} />
        </>
      );
    default:
      return <p>Hmm...</p>;
  }
}

export default ActionMenuContainer;
