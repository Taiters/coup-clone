import { socket } from "../socket";
import { Game, Player, TurnAction } from "../types";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";

type Props = {
  currentPlayer: Player;
  game: Game;
};

function AttemptedActionMenu({ game, currentPlayer }: Props) {
  if (currentPlayer.isCurrentTurn) {
    return (
      <p>
        You've attempted {TurnAction[game.turnAction]}
        {game.turnTarget && ` against ${game.turnTarget.name}`}
      </p>
    );
  }

  return (
    <VGroup>
      <p>
        {game.currentTurn.name} has attempted {TurnAction[game.turnAction]}
        {game.turnTarget && ` against ${game.turnTarget.name}`}
      </p>
      <Button label="accept" onClick={() => socket.emit("accept_action")} />
    </VGroup>
  );
}

export default AttemptedActionMenu;
