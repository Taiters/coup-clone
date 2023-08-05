import { FaUser } from "react-icons/fa6";
import { GiTwoCoins } from "react-icons/gi";
import Flex from "./Flex";
import styles from "./PlayerInfo.module.css";

type Props = {
    name: string,
    influence: PlayerInfluenceType[],
    isConnected: boolean,
    color: string,
    coins: number,
    isCurrentTurn: boolean,
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
    color,
    coins,
    isCurrentTurn,
}: Props) {
    return (
        <div className={styles.container}>
            <Flex alignItems="center">
                <FaUser color={color} />
                <span className={styles.name} style={{ color }}>{name}</span>
                {isCurrentTurn ? (
                    <span className={styles.turn}>
                        (Current turn)
                    </span>
                ) : null}
                <div className={styles.right}>
                    <Flex direction="column" alignItems="flex-end">
                        {influence.map((infl, i) => (
                            <span className={`${styles.influence} ${styles[infl.toLowerCase()]}`}>{infl}</span>
                        ))}
                    </Flex>
                </div>
                <span className={styles.coins}>{coins}</span>
                <GiTwoCoins />
                <div className={styles.connection} style={{
                    backgroundColor: isConnected ? "#7eff7e" : "#fe5151"
                }} />
            </Flex>
        </div>
    )
}

export default PlayerInfo;