import styles from "./GameLogMessage.module.css";

type Props = {
    message: string,
}

function GameLogMessage({message}: Props) {
    return (
        <div className={styles.container}>
            <p className={styles.message}>{message}</p>
        </div>
    )
}

export default GameLogMessage;