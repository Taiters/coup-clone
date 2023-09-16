import { useEventEmitter } from "../socket";
import { Game, Player } from "../types";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";

type Props = {
  game: Game;
  currentPlayer: Player;
};

function FinishedGameTurnMenu({ game, currentPlayer }: Props) {
  const [emitRestart, isRestartInFlight] = useEventEmitter("restart");

  return (
    <VGroup>
      <p>{game.winner?.name ?? "UNKNOWN"} has won the game!</p>
      {currentPlayer.host && (
        <Button
          label="Restart"
          onClick={() => emitRestart()}
          pending={isRestartInFlight}
        />
      )}
    </VGroup>
  );
}

export default FinishedGameTurnMenu;
