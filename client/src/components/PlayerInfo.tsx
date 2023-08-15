import Coins from "./ui/Coins";
import HGroup from "./layout/HGroup";
import Influence from "./ui/Influence";
import PlayerName from "./ui/PlayerName";
import { Player, PlayerInfluence } from "../types";

type Props = {
  player: Player,
};

function PlayerInfo({ player }: Props) {
  return (
    <HGroup>
      <div style={{ width: "45%" }}>
        <PlayerName name={player.name} />
      </div>
      <Coins value={player.coins} />
      <div style={{ width: "25%" }}>
        <Influence influence={player.influence[0]} />
      </div>
      <div style={{ width: "25%" }}>
        <Influence influence={player.influence[1]} />
      </div>
    </HGroup>
  );
}

export default PlayerInfo;
