import { useEventEmitter } from "../socket";
import { Game, Player } from "../types";
import { nullthrows } from "../utils";
import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";

type Props = {
  currentPlayer: Player;
  game: Game;
};

function BlockedMenu({ game, currentPlayer }: Props) {
  const blocker = nullthrows(game.turnBlocker);
  const emitEvent = useEventEmitter();

  if (blocker.id === currentPlayer.id) {
    return <p>You've blocked {nullthrows(game.currentTurn?.name)}</p>;
  }

  return (
    <VGroup>
      <p>
        {blocker.name} has blocked{" "}
        {nullthrows(game.currentTurn?.id) === currentPlayer.id
          ? "you"
          : nullthrows(game.currentTurn?.name)}
      </p>
      <HGroup>
        {nullthrows(game.currentTurn?.id) === currentPlayer.id && (
          <Button
            className="w-full"
            label="Accept"
            onClick={() => emitEvent("accept_block")}
          />
        )}
        <Button
          className="w-full"
          label="Challenge"
          onClick={() => emitEvent("challenge_block")}
        />
      </HGroup>
    </VGroup>
  );
}

export default BlockedMenu;
