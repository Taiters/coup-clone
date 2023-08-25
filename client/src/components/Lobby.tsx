import Button from "./ui/Button";
import Container from "./layout/Container";
import LobbyPlayer from "./LobbyPlayer";
import PageTitle from "./ui/PageTitle";
import VGroup from "./layout/VGroup";
import { Game, Player, PlayerState } from "../types";
import { FaShare } from "react-icons/fa6";
import LinkButton from "./ui/LinkButton";
import { socket } from "../socket";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
  onStart: () => void;
};

function Lobby({ game, players, currentPlayer, onStart }: Props) {
  const lobbyPlayers = players.map((p, i) => (
    <LobbyPlayer key={i} player={p} current={currentPlayer.id === p.id} />
  ));
  while (lobbyPlayers.length < 6) {
    lobbyPlayers.push(<LobbyPlayer key={lobbyPlayers.length} />);
  }

  const readyToStart =
    players.filter((p) => p.state === PlayerState.READY).length >= 2;

  const canShare = navigator.share != null;

  const onShare = () => {
    navigator.share({
      url: window.location.href,
      title: "Come play coup",
      text: "Game Code: " + game.id,
    });
  };

  const onLeave = () => {
    socket.emit("leave_game");
  };

  return (
    <Container>
      <PageTitle
        heading="Lobby"
        subheading={
          <span>
            Code: {game.id} {canShare && <FaShare onClick={onShare} />}
          </span>
        }
      />
      <VGroup className="mb-10">{lobbyPlayers}</VGroup>
      <VGroup>
        {currentPlayer.host ? (
          <Button disabled={!readyToStart} label="Start" onClick={onStart} />
        ) : (
          <p className="text-center m-0 text-brown">Waiting for host...</p>
        )}
        <LinkButton className="mt-8" onClick={onLeave} label="Leave game" />
      </VGroup>
    </Container>
  );
}

export default Lobby;
