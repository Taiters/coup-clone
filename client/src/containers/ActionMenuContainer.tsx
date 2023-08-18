import CurrentTurn from "../components/CurrentTurn";
import WaitingForPlayer from "../components/WaitingForPlayer";
import { Game, Player, TurnAction, TurnState } from "../types";


type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function ActionMenuContainer({game, players, currentPlayer}: Props) {
  if (currentPlayer.isCurrentTurn) {
    return <CurrentTurn />
  }

  switch (game.turnState) {
    case TurnState.START:
      return <WaitingForPlayer player={game.currentTurn} />;
    case TurnState.ATTEMPTED:
      return <p>{game.currentTurn.name} has attempted {TurnAction[game.turnAction]}</p>
    default:
      return <p>Hmm...</p>
  }
}

export default ActionMenuContainer;
