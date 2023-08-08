import {FaUser} from 'react-icons/fa6';
import PlayerName from "./PlayerName";
import styles from "./LobbyPlayer.module.css";
import HGroup from "./HGroup";

type Props = {
    name?: string | undefined,
}

function LobbyPlayer({name}: Props) {
    return (
        <div className={styles.container}>
            {name != null ? <PlayerName name={name} /> : (
                <HGroup className={styles.pending}>
                    <FaUser />
                    Waiting for player...
                </HGroup>
            )}
        </div>
    )
}

export default LobbyPlayer;