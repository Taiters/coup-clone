import {FaUser} from "react-icons/fa6";
import Flex from "./Flex";
import styles from "./PlayerInfo.module.css";

type Props = {
    name: string,
    influence: PlayerInfluenceType[],
    isConnected: boolean,
}

export enum PlayerInfluenceType {
    UNKNOWN = "UNKNOWN",
    DUKE = "DUKE",
    ASSASSIN = "ASSASSIN",
    CAPTAIN = "CAPTAIN",
    CONTESSA = "CONTESSA",
    AMBASSADOR = "AMBASSADOR",
}

function PlayerInfo({
    name,
    influence, 
    isConnected,
}: Props) {
    return (
        <div className={!isConnected ? styles.disconnected : undefined}>
            <Flex alignItems="center">
                <FaUser color={isConnected ? '#46c946' : '#ff4949'} />
                <span>{name}</span>
                <div className={styles.right}>
                    <Flex alignItems="center">
                        {influence.map((infl, i) => (
                            <span className={`${styles.influence} ${styles[infl.toLowerCase()]}`}>{infl}</span>
                        ))}
                    </Flex>
                </div>
            </Flex>
        </div>
    )
}

export default PlayerInfo;