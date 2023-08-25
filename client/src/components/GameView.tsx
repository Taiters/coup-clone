import Container from "./layout/Container";
import TopBar from "./ui/TopBar";
import PlayerInfo from "./PlayerInfo";
import { Game, GameEvent, GameState, Player, PlayerInfluence } from "../types";
import VGroup from "./layout/VGroup";
import GameLog from "./GameLog";
import TurnMenuContainer from "../containers/TurnMenuContainer";
import { socket } from "../socket";
import LinkButton from "./ui/LinkButton";
import HGroup from "./layout/HGroup";
import { FaBars } from "react-icons/fa6";
import { useState } from "react";
import Modal from "./ui/Modal";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameView({ game, players, events, currentPlayer }: Props) {
  const [menuOpen, setMenuOpen] = useState(false);
  const otherPlayers = players.filter((p) => p.id !== currentPlayer.id);

  const onLeave = () => {
    socket.emit("leave_game");
  };

  return (
    <>
      <div className="h-full flex flex-col">
        <TopBar>
          <LinkButton
            className="max-sm:hidden ml-2 float-left"
            onClick={() => setMenuOpen((open) => !open)}
            label="Menu"
          />
          <Container>
            <HGroup>
              <PlayerInfo player={currentPlayer} />
              <FaBars
                className="max-sm:visible sm:hidden text-3xl cursor-pointer"
                onClick={() => setMenuOpen((open) => !open)}
              />
            </HGroup>
          </Container>
        </TopBar>
        <div className="py-4 bg-darkyellow">
          <Container>
            <VGroup>
              {otherPlayers.map((p) => (
                <PlayerInfo key={p.id} player={p} />
              ))}
            </VGroup>
          </Container>
        </div>
        <div className="border-y border-solid border-y-darkbrown bg-darkeryellow flex-grow overflow-y-auto">
          <Container>
            <GameLog events={events} />
          </Container>
        </div>
        <div className="py-2 text-center">
          <Container>
            {game.state === GameState.RUNNING ? (
              currentPlayer.influenceA !== PlayerInfluence.UNKNOWN &&
              currentPlayer.influenceB !== PlayerInfluence.UNKNOWN ? (
                <p>You are out</p>
              ) : (
                <TurnMenuContainer
                  game={game}
                  players={players}
                  currentPlayer={currentPlayer}
                />
              )
            ) : (
              <p>{game.winner?.name ?? "UNKNOWN"} has won the game!</p>
            )}
          </Container>
        </div>
      </div>
      {menuOpen && (
        <Modal heading="Menu" onClose={() => setMenuOpen(false)}>
          <VGroup>
            <LinkButton label="Leave Game" onClick={onLeave} />
          </VGroup>
        </Modal>
      )}
    </>
  );
}

export default GameView;
