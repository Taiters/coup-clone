import Button from "./ui/Button";
import Container from "./layout/Container";
import LobbyPlayer from "./LobbyPlayer";
import PageTitle from "./ui/PageTitle";
import VGroup from "./layout/VGroup";
import { Game, Player, PlayerState } from "../types";
import { FaShare } from "react-icons/fa6";
import LinkButton from "./ui/LinkButton";
import { useEventEmitter } from "../socket";
import { useState } from "react";
import Modal from "./ui/Modal";
import Help from "./Help";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function Lobby({ game, players, currentPlayer }: Props) {
  const [showHelp, setShowHelp] = useState(false);
  const [emitLeaveGame, isLeaveGameInFlight] = useEventEmitter("leave_game");
  const [emitStartgame, isStartGameInFlight] = useEventEmitter("start_game");

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

  const onLeave = () => emitLeaveGame();
  const onStart = () => emitStartgame();

  return (
    <>
      <Container>
        <PageTitle
          heading="Lobby"
          subheading={
            <span>
              Code: {game.id}{" "}
              {canShare && (
                <FaShare className="inline cursor-pointer" onClick={onShare} />
              )}
            </span>
          }
        />
        <VGroup className="mb-10">{lobbyPlayers}</VGroup>
        <VGroup>
          {currentPlayer.host ? (
            <Button
              disabled={!readyToStart}
              label="Start"
              onClick={onStart}
              pending={isStartGameInFlight}
            />
          ) : (
            <p className="text-center m-0 text-brown">Waiting for host...</p>
          )}
          <LinkButton
            className="mx-auto !block text-center"
            onClick={() => setShowHelp(true)}
            label="How to play"
          />
          <LinkButton
            className="text-center mt-8"
            onClick={onLeave}
            pending={isLeaveGameInFlight}
            label="Leave game"
          />
        </VGroup>
      </Container>
      {showHelp && (
        <Modal heading="How to play" onClose={() => setShowHelp(false)}>
          <Help />
        </Modal>
      )}
    </>
  );
}

export default Lobby;
