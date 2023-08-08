import { useState } from "react";
import Lobby from "./Lobby";
import Container from "./Container";
import TopBar from "./TopBar";
import PlayerInfo from "./PlayerInfo";
import { InfluenceType } from "./Influence";
import VGroup from "./VGroup";
import styles from "./Game.module.css";
import Button from "./Button";
import HGroup from "./HGroup";
import GameLog from "./GameLog";

function Game() {
    const [started, setStarted] = useState<boolean>(false);

    return !started 
        ? <Lobby onStart={() => setStarted(true)} />
        : (
            <div className={styles.verticalContainer}>
                <TopBar>
                    <Container>
                        <PlayerInfo 
                            name="Danny Boy"
                            coins={5}
                            influence={[InfluenceType.AMBASSADOR, InfluenceType.AMBASSADOR]} />
                    </Container>
                </TopBar>
                <div className={styles.players}>
                    <Container>
                        <VGroup>
                            <PlayerInfo 
                                name="Snejy Meche"
                                coins={12}
                                influence={[InfluenceType.UNKNOWN, InfluenceType.DUKE]} />
                            <PlayerInfo 
                                name="Walter White"
                                coins={4}
                                influence={[InfluenceType.ASSASSIN, InfluenceType.AMBASSADOR]} />
                            <PlayerInfo 
                                name="Jesse Pinkman"
                                coins={12}
                                influence={[InfluenceType.CAPTAIN, InfluenceType.UNKNOWN]} />
                            <PlayerInfo 
                                name="Snejy Meche"
                                coins={12}
                                influence={[InfluenceType.UNKNOWN, InfluenceType.DUKE]} />
                        </VGroup>
                    </Container>
                </div>
                <div className={styles.log}>
                    <Container>
                        <GameLog />
                    </Container>
                </div>
                <div className={styles.controls}>
                    <Container>
                        <VGroup>
                            <HGroup>
                                <VGroup className={styles.buttonStack}>
                                    <Button label="Income" />
                                    <Button label="Tax" />
                                    <Button label="Exchange" />
                                </VGroup>
                                <VGroup className={styles.buttonStack}>
                                    <Button label="Foreign Aid" />
                                    <Button label="Assassinate" />
                                    <Button label="Steal" />
                                </VGroup>
                            </HGroup>
                            <Button label="Coup" />
                        </VGroup>
                    </Container>
                </div>
            </div>
        );
}

export default Game;