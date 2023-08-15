import Container from "./layout/Container";
import TopBar from "./ui/TopBar";
import PlayerInfo from "./PlayerInfo";
import { Game, GameEvent, Player } from "../types";
import VGroup from "./layout/VGroup";
import styles from "./GameView.module.css";
import Button from "./ui/Button";
import HGroup from "./layout/HGroup";
import GameLog from "./GameLog";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameView({ game, players, events, currentPlayer }: Props) {
  const otherPlayers = players.filter((p) => p.id !== currentPlayer.id);
  return (
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

export default GameView;
