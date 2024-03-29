import Container from "./layout/Container";
import TopBar from "./ui/TopBar";
import PlayerInfo from "./PlayerInfo";
import { Game, GameEvent, Player } from "../types";
import VGroup from "./layout/VGroup";
import GameLog from "./GameLog";
import TurnMenuContainer from "../containers/TurnMenuContainer";
import { useEventEmitter } from "../socket";
import LinkButton from "./ui/LinkButton";
import HGroup from "./layout/HGroup";
import { FaBars } from "react-icons/fa6";
import { useState } from "react";
import Modal from "./ui/Modal";
import Help from "./Help";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameView({ game, players, events, currentPlayer }: Props) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [emitLeaveGame, isLeaveGameInFlight] = useEventEmitter("leave_game");

  const otherPlayers = players.filter((p) => p.id !== currentPlayer.id);

  const onLeave = () => emitLeaveGame();

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
            <TurnMenuContainer
              game={game}
              players={players}
              currentPlayer={currentPlayer}
            />
          </Container>
        </div>
      </div>
      {menuOpen && (
        <Modal heading="Menu" onClose={() => setMenuOpen(false)}>
          <VGroup className="p-1">
            <LinkButton
              label="How to play"
              onClick={() => {
                setMenuOpen(false);
                setShowHelp(true);
              }}
            />
            <LinkButton
              label="Leave Game"
              onClick={onLeave}
              pending={isLeaveGameInFlight}
            />
          </VGroup>
        </Modal>
      )}
      {showHelp && (
        <Modal heading="How to play" onClose={() => setShowHelp(false)}>
          <Help />
        </Modal>
      )}
    </>
  );
}

export default GameView;
