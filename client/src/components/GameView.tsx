import Container from "./layout/Container";
import TopBar from "./ui/TopBar";
import PlayerInfo from "./PlayerInfo";
import { Action, Game, GameEvent, Player } from "../types";
import VGroup from "./layout/VGroup";
import styles from "./GameView.module.css";
import Button from "./ui/Button";
import HGroup from "./layout/HGroup";
import GameLog from "./GameLog";
import { socket } from "../socket";
import Countdown from "./ui/Countdown";
import ActionMenu from "./ActionMenu";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameView({ game, players, events, currentPlayer }: Props) {
  const otherPlayers = players.filter((p) => p.id !== currentPlayer.id);

  const turnStateModified = game.turnStateModified;
  const turnStateDeadline = game.turnStateDeadline;
  return (
    <>
      <div className={styles.verticalContainer}>
        <TopBar>
          <Container>
            <PlayerInfo player={currentPlayer} />
          </Container>
        </TopBar>
        <div className={styles.players}>
          <Container>
            <VGroup>
              {otherPlayers.map((p) => (
                <PlayerInfo key={p.id} player={p} />
              ))}
            </VGroup>
          </Container>
        </div>
        <div className={styles.log}>
          <Container>
            <GameLog events={events} />
          </Container>
        </div>
        <div className={styles.controls}>
          <Container>
            <ActionMenu />
          </Container>
        </div>
      </div>
      {turnStateModified && turnStateDeadline && <Countdown from={turnStateModified} to={turnStateDeadline} />}
    </>
  );
}

export default GameView;
