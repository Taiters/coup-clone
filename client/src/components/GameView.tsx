import Container from "./layout/Container";
import TopBar from "./ui/TopBar";
import PlayerInfo from "./PlayerInfo";
import { Game, GameEvent, GameState, Player, PlayerInfluence } from "../types";
import VGroup from "./layout/VGroup";
import GameLog from "./GameLog";
import TurnMenuContainer from "../containers/TurnMenuContainer";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameView({ game, players, events, currentPlayer }: Props) {
  const otherPlayers = players.filter((p) => p.id !== currentPlayer.id);

  return (
    <>
      <div className="h-full flex flex-col">
        <TopBar>
          <Container>
            <PlayerInfo player={currentPlayer} />
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
    </>
  );
}

export default GameView;
