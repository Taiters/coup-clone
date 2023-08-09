import Coins from "./Coins";
import HGroup from "./HGroup";
import Influence from "./Influence";
import PlayerName from "./PlayerName";
import { PlayerInfluence } from "./types";

type Props = {
    name: string,
    coins: number,
    influence: PlayerInfluence[],
}

function PlayerInfo({name, coins, influence}: Props) {
    return (
        <HGroup>
            <div style={{width: "45%"}}>
                <PlayerName name={name} />
            </div>
            <Coins value={coins} />
            <div style={{width: "25%"}}>
                <Influence influence={influence[0]} />
            </div>
            <div style={{width: "25%"}}>
                <Influence influence={influence[1]} />
            </div>
        </HGroup>
    );
}

export default PlayerInfo;