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
import Countdown from "./ui/Coutdown";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameView({ game, players, events, currentPlayer }: Props) {
  const otherPlayers = players.filter((p) => p.id !== currentPlayer.id);
  const deadline = game.turnStateDeadline;
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
        <p>Countdown: {deadline ? <Countdown to={deadline} /> : 'N/A'}</p>
        </Container>
      </div>
      <div className={styles.log}>
        <Container>
          <GameLog events={events} />
        </Container>
      </div>
      <div className={styles.controls}>
        <Container>
          <VGroup>
            <HGroup>
              <VGroup className={styles.buttonStack}>
                <Button
                  label="Income"
                  onClick={() =>
                    socket.emit("take_action", { action: Action.INCOME })
                  }
                />
                <Button
                  label="Tax"
                  onClick={() =>
                    socket.emit("take_action", { action: Action.TAX })
                  }
                />
                <Button
                  label="Exchange"
                  onClick={() =>
                    socket.emit("take_action", { action: Action.EXCHANGE })
                  }
                />
              </VGroup>
              <VGroup className={styles.buttonStack}>
                <Button
                  label="Foreign Aid"
                  onClick={() =>
                    socket.emit("take_action", { action: Action.FOREIGN_AID })
                  }
                />
                <Button
                  label="Assassinate"
                  onClick={() =>
                    socket.emit("take_action", { action: Action.ASSASSINATE })
                  }
                />
                <Button
                  label="Steal"
                  onClick={() =>
                    socket.emit("take_action", { action: Action.STEAL })
                  }
                />
              </VGroup>
            </HGroup>
            <Button
              label="Coup"
              onClick={() =>
                socket.emit("take_action", { action: Action.COUP })
              }
            />
          </VGroup>
        </Container>
      </div>
    </div>
  );
}

export default GameView;
