import { socket } from "../socket";
import { Player, PlayerInfluence } from "../types";
import { nullthrows } from "../utils";
import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import InfluenceButton from "./ui/InfluenceButton";

type Props = {
  playerToReveal: Player;
  currentPlayer: Player;
};

function RevealingActionMenu({ playerToReveal, currentPlayer }: Props) {
  if (playerToReveal.id !== currentPlayer.id) {
    return <p>Waiting for {playerToReveal.name} to reveal an influence</p>;
  }

  const hand = nullthrows(currentPlayer.hand);

  return (
    <VGroup>
      <p>You must reveal an influence</p>
      <HGroup>
        <InfluenceButton
          className="w-full"
          influence={hand.influenceA}
          disabled={currentPlayer.influenceA !== PlayerInfluence.UNKNOWN}
          onClick={() => socket.emit("reveal", hand.influenceA)}
        />
        <InfluenceButton
          className="w-full"
          influence={hand.influenceB}
          disabled={currentPlayer.influenceB !== PlayerInfluence.UNKNOWN}
          onClick={() => socket.emit("reveal", hand.influenceB)}
        />
      </HGroup>
    </VGroup>
  );
}

export default RevealingActionMenu;
