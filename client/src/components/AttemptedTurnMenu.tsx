import { socket } from "../socket";
import { Game, Player, TurnAction } from "../types";
import { titleCase } from "../utils";
import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";

type Props = {
  currentPlayer: Player;
  game: Game;
};

function AttemptedTurnMenu({ game, currentPlayer }: Props) {
  if (currentPlayer.isCurrentTurn) {
    return (
      <p>
        You've attempted <span className="italic">{titleCase(TurnAction[game.turnAction])}</span>
        {game.turnTarget && ` against ${game.turnTarget.name}`}
      </p>
    );
  }

  const canBlock =
    game.turnAction === TurnAction.FOREIGN_AID ||
    (game.turnTarget?.id === currentPlayer.id &&
      (game.turnAction === TurnAction.STEAL ||
        game.turnAction === TurnAction.ASSASSINATE));
    
  const canChallenge =
    game.turnAction !== TurnAction.FOREIGN_AID &&
    game.turnAction !== TurnAction.INCOME &&
    game.turnAction !== TurnAction.COUP;

  return (
    <VGroup>
      <p>
        {game.currentTurn.name} has attempted <span className="italic">{TurnAction[game.turnAction]}</span>
        {game.turnTarget && ` against ${game.turnTarget.name}`}
      </p>
      <HGroup>
        <Button className="w-full" label="Accept" onClick={() => socket.emit("accept_action")} />
        {canChallenge &&
          <Button className="w-full" label="Challenge" onClick={() => socket.emit("challenge")} />
        }
        {canBlock && (
          <Button className="w-full" label="Block" onClick={() => socket.emit("block")} />
        )}
      </HGroup>
    </VGroup>
  );
}

export default AttemptedTurnMenu;
