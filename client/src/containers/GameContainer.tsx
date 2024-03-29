import GameView from "../components/GameView";
import Join from "../components/Join";
import Lobby from "../components/Lobby";
import { Game, GameEvent, GameState, Player, PlayerState } from "../types";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameContainer({ game, players, events, currentPlayer }: Props) {
  if (currentPlayer.state === PlayerState.PENDING) {
    return <Join />;
  }

  switch (game.state) {
    case GameState.LOBBY:
      return (
        <Lobby game={game} players={players} currentPlayer={currentPlayer} />
      );
    case GameState.RUNNING:
      return (
        <GameView
          game={game}
          players={players}
          events={events}
          currentPlayer={currentPlayer}
        />
      );
    case GameState.FINISHED:
      return (
        <GameView
          game={game}
          players={players}
          events={events}
          currentPlayer={currentPlayer}
        />
      );
  }
}

export default GameContainer;
