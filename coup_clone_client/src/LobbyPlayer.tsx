import {FaUser} from 'react-icons/fa6';
import PlayerName from "./PlayerName";
import styles from "./LobbyPlayer.module.css";
import HGroup from "./HGroup";
import { Player, PlayerState } from './types';

type Props = {
    player?: Player,
}

function LobbyPlayer({
    player,
}: Props) {
    if (player == null) {
        return (
            <div className={styles.container}>
                <HGroup className={styles.pending}>
                    <FaUser />
                    Waiting for player...
                </HGroup>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            {player.state == PlayerState.JOINED ? <PlayerName name={player.name} /> : (
                <HGroup className={styles.pending}>
                    <FaUser />
                    Joining...
                </HGroup>
            )}
        </div>
    )
}

export default LobbyPlayer;