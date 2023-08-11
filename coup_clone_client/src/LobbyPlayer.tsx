import {FaUser} from 'react-icons/fa6';
import PlayerName from "./PlayerName";
import styles from "./LobbyPlayer.module.css";
import HGroup from "./HGroup";
import { Player, PlayerState } from './types';

type Props = {
    player?: Player,
    current?: boolean,
}

function LobbyPlayer({
    player,
    current = false,
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
            {player.state == PlayerState.JOINED ?<div className={current ? styles.current : undefined}><PlayerName name={player.name} /></div> : (
                <HGroup className={styles.pending}>
                    <FaUser />
                    Joining...
                </HGroup>
            )}
        </div>
    )
}

export default LobbyPlayer;