import Button from "./Button";
import Container from "./Container";
import LobbyPlayer from "./LobbyPlayer";
import PageTitle from "./PageTitle";
import VGroup from "./VGroup";
import styles from "./Lobby.module.css";
import { Player } from "./types";
import { socket } from "./socket";
import LeaveButton from "./LeaveButton";

type Props = {
    players: Player[],
    isHost: boolean,
    onStart: () => void,
}

function Lobby({players, isHost, onStart}: Props) {
    const lobbyPlayers = players.map((p, i) => <LobbyPlayer key={i} player={p} />);
    while (lobbyPlayers.length < 6) {
        lobbyPlayers.push(<LobbyPlayer key={lobbyPlayers.length} />);
    }

    return (
        <Container>
            <PageTitle heading="Lobby" subheading="Code: 123ABC" />
            <VGroup className={styles.players}>
                {lobbyPlayers}
            </VGroup>
            <VGroup>
                {isHost 
                    ? <Button label="Start" onClick={onStart} />
                    : <p className={styles.waiting}>Waiting for host...</p>
                }
                <LeaveButton />
            </VGroup>
        </Container>
    )
}

export default Lobby;