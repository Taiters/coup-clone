import { socket } from "../socket";
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
  if (blocker.id === currentPlayer.id) {
    return <p>You've blocked {game.currentTurn.name}</p>;
  }

  return (
    <VGroup>
      <p>
        {blocker.name} has blocked{" "}
        {game.currentTurn.id === currentPlayer.id
          ? "you"
          : game.currentTurn.name}
      </p>
      <HGroup>
        {game.currentTurn.id === currentPlayer.id && (
          <Button className="w-full" label="Accept" onClick={() => socket.emit("accept_block")} />
        )}
        <Button
          className="w-full"
          label="Challenge"
          onClick={() => socket.emit("challenge_block")}
        />
      </HGroup>
    </VGroup>
  );
}

export default BlockedMenu;
