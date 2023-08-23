import Coins from "./ui/Coins";
import HGroup from "./layout/HGroup";
import Influence from "./ui/Influence";
import PlayerName from "./ui/PlayerName";
import { Player, PlayerInfluence } from "../types";
import styles from "./PlayerInfo.module.css";

type Props = {
  player: Player;
};

function PlayerInfo({ player }: Props) {
  const isOut =
    player.influenceA !== PlayerInfluence.UNKNOWN &&
    player.influenceB !== PlayerInfluence.UNKNOWN;
  return (
    <HGroup className={isOut ? styles.out : undefined}>
      <div style={{ width: "45%" }}>
        <PlayerName name={player.name} isCurrentTurn={player.isCurrentTurn} />
      </div>
      <Coins value={player.coins} />
      <div style={{ width: "25%" }}>
        <Influence
          revealed={!isOut && player.influenceA !== PlayerInfluence.UNKNOWN}
          influence={player.hand?.influenceA ?? player.influenceA}
        />
      </div>
      <div style={{ width: "25%" }}>
        <Influence
          revealed={!isOut && player.influenceB !== PlayerInfluence.UNKNOWN}
          influence={player.hand?.influenceB ?? player.influenceB}
        />
      </div>
    </HGroup>
  );
}

export default PlayerInfo;
