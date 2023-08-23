import { socket } from "../socket";
import { Game, Player, TurnAction } from "../types";
import HGroup from "./layout/HGroup";
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
      <HGroup>
        <Button label="Accept" onClick={() => socket.emit("accept_action")} />
        <Button label="Challenge" onClick={() => socket.emit("challenge")} />
      </HGroup>
    </VGroup>
  );
}

export default AttemptedActionMenu;
