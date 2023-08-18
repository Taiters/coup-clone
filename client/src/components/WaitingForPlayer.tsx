import { Player } from "../types";

type Props = {
    player: Player;
}

function WaitingForPlayer({player}: Props) {
    return <span>Waiting for {player.name}</span>
}

export default WaitingForPlayer;