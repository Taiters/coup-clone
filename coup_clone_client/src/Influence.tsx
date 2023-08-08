import styles from "./Influence.module.css"

export enum InfluenceType {
    UNKNOWN,
    AMBASSADOR,
    ASSASSIN,
    CAPTAIN,
    DUKE,
    CONTESSA,
}

const INFLUENCE_COLORS = {
    [InfluenceType.UNKNOWN]: "#8E8D7E",
    [InfluenceType.AMBASSADOR]: "#ADB55A",
    [InfluenceType.ASSASSIN]: "#689393",
    [InfluenceType.CAPTAIN]: "#4494DE",
    [InfluenceType.DUKE]: "#BF7BDF",
    [InfluenceType.CONTESSA]: "#DA7777",
}

const INFLUENCE_NAMES = {
    [InfluenceType.UNKNOWN]: "???",
    [InfluenceType.AMBASSADOR]: "AMBASSADOR",
    [InfluenceType.ASSASSIN]: "ASSASSIN",
    [InfluenceType.CAPTAIN]: "CAPTAIN",
    [InfluenceType.DUKE]: "DUKE",
    [InfluenceType.CONTESSA]: "CONTESSA",
}

type Props = {
    influence: InfluenceType,
}

function Influence({influence}: Props) {
    const isUnknown = influence === InfluenceType.UNKNOWN;
    return (
        <div className={styles.influence} style={{
            color: INFLUENCE_COLORS[influence],
            // WebkitTextStroke: isUnknown ? undefined : "0.25px black",
        }}>{INFLUENCE_NAMES[influence]}</div>
    )
}

export default Influence;