import Coins from "./ui/Coins";
import HGroup from "./layout/HGroup";
import Influence from "./ui/Influence";
import PlayerName from "./ui/PlayerName";
import { PlayerInfluence } from "../types";

type Props = {
  name: string;
  coins: number;
  influence: PlayerInfluence[];
};

function PlayerInfo({ name, coins, influence }: Props) {
  return (
    <HGroup>
      <div style={{ width: "45%" }}>
        <PlayerName name={name} />
      </div>
      <Coins value={coins} />
      <div style={{ width: "25%" }}>
        <Influence influence={influence[0]} />
      </div>
      <div style={{ width: "25%" }}>
        <Influence influence={influence[1]} />
      </div>
    </HGroup>
  );
}

export default PlayerInfo;
