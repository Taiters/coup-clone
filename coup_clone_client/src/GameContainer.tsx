import { useEffect, useState } from "react";
import Lobby from "./Lobby";
import Container from "./Container";
import TopBar from "./TopBar";
import PlayerInfo from "./PlayerInfo";
import { Game, GameEvent, Player, PlayerInfluence, PlayerState } from "./types";
import VGroup from "./VGroup";
import styles from "./GameContainer.module.css";
import Button from "./Button";
import HGroup from "./HGroup";
import GameLog from "./GameLog";
import { useParams } from "react-router-dom";
import Join from "./Join";
import { socket } from "./socket";


export type GameState = {
    game: Game | null,
    players: Player[],
    events: GameEvent[],
    currentPlayer: Player | null,
}


function GameContainer() {
    const {gameID} = useParams();
    const [game, setGame] = useState<Game | null>(null);
    const [players, setPlayers] = useState<Player[]>([]);
    const [events, setEvents] = useState<GameEvent[]>([]);
    const [currentPlayer, setCurrentPlayer] = useState<Player | null>(null);
    const [started, setStarted] = useState(false);

    useEffect(() => {
        socket.connect();
        socket.timeout(5000).emitWithAck('enter_game', gameID)
            .then(({
                game,
                players,
                currentPlayer
            }: {
                game: Game,
                players: Player[],
                events: GameEvent[],
                currentPlayer: Player
            }) => {
                setGame(game);
                setPlayers(players);
                setEvents(events);
                setCurrentPlayer(currentPlayer);
            });
    }, [gameID]);

    useEffect(() => {
        const handlePlayersUpdate = (players: Player[]) => {
            setPlayers(players);
            setCurrentPlayer(currentPlayer => players.find(p => p.id === currentPlayer?.id) ?? null);
        }

        socket.on('update_players', handlePlayersUpdate);
        return () => {
            socket.off('update_players', handlePlayersUpdate);
        }
    }, [setPlayers, setCurrentPlayer])

    if (currentPlayer == null) {
        return <h1>Joining</h1>;
    }


    if (currentPlayer != null && currentPlayer.state === PlayerState.JOINING) {
        return <Join />
    }

    return !started 
        ? <Lobby players={players} isHost={true} onStart={() => setStarted(true)} />
        : (
            <div className={styles.verticalContainer}>
                <TopBar>
                    <Container>
                        <PlayerInfo 
                            name="Danny Boy"
                            coins={5}
                            influence={[PlayerInfluence.AMBASSADOR, PlayerInfluence.AMBASSADOR]} />
                    </Container>
                </TopBar>
                <div className={styles.players}>
                    <Container>
                        <VGroup>
                            <PlayerInfo 
                                name="Snejy Meche"
                                coins={12}
                                influence={[PlayerInfluence.UNKNOWN, PlayerInfluence.DUKE]} />
                            <PlayerInfo 
                                name="Walter White"
                                coins={4}
                                influence={[PlayerInfluence.ASSASSIN, PlayerInfluence.AMBASSADOR]} />
                            <PlayerInfo 
                                name="Jesse Pinkman"
                                coins={12}
                                influence={[PlayerInfluence.CAPTAIN, PlayerInfluence.UNKNOWN]} />
                            <PlayerInfo 
                                name="Snejy Meche"
                                coins={12}
                                influence={[PlayerInfluence.UNKNOWN, PlayerInfluence.DUKE]} />
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

export default GameContainer;