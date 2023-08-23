import Coins from "./ui/Coins";
import HGroup from "./layout/HGroup";
import Influence from "./ui/Influence";
import PlayerName from "./ui/PlayerName";
import { Player, PlayerInfluence } from "../types";

type Props = {
  player: Player;
};

function PlayerInfo({ player }: Props) {
  return (
    <HGroup>
      <div style={{ width: "45%" }}>
        <PlayerName name={player.name} isCurrentTurn={player.isCurrentTurn} />
      </div>
      <Coins value={player.coins} />
      <div style={{ width: "25%" }}>
        <Influence
          revealed={player.influenceA !== PlayerInfluence.UNKNOWN}
          influence={player.hand?.influenceA ?? player.influenceA}
        />
      </div>
      <div style={{ width: "25%" }}>
        <Influence
          revealed={player.influenceB !== PlayerInfluence.UNKNOWN}
          influence={player.hand?.influenceB ?? player.influenceB}
        />
      </div>
    </HGroup>
  );
}

export default PlayerInfo;
