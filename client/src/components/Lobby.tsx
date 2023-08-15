import Button from "./ui/Button";
import Container from "./layout/Container";
import LobbyPlayer from "./LobbyPlayer";
import PageTitle from "./ui/PageTitle";
import VGroup from "./layout/VGroup";
import styles from "./Lobby.module.css";
import { Player, PlayerState } from "../types";
import LeaveButton from "./LeaveButton";

type Props = {
  players: Player[];
  currentPlayer: Player;
  onStart: () => void;
};

function Lobby({ players, currentPlayer, onStart }: Props) {
  const lobbyPlayers = players.map((p, i) => (
    <LobbyPlayer key={i} player={p} current={currentPlayer.id === p.id} />
  ));
  while (lobbyPlayers.length < 6) {
    lobbyPlayers.push(<LobbyPlayer key={lobbyPlayers.length} />);
  }

  const readyToStart = players.filter(p => p.state === PlayerState.READY).length >= 2;

  return (
    <Container>
      <PageTitle heading="Lobby" subheading="Code: 123ABC" />
      <VGroup className={styles.players}>{lobbyPlayers}</VGroup>
      <VGroup>
        {currentPlayer.host ? (
          <Button disabled={!readyToStart} label="Start" onClick={onStart} />
        ) : (
          <p className={styles.waiting}>Waiting for host...</p>
        )}
        <LeaveButton />
      </VGroup>
    </Container>
  );
}

export default Lobby;
