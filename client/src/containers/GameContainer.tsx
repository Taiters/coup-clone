import Join from "../components/Join";
import Lobby from "../components/Lobby";
import { socket } from "../socket";
import { Game, GameEvent, GameState, Player, PlayerState } from "../types";

type Props = {
  game: Game;
  players: Player[];
  events: GameEvent[];
  currentPlayer: Player;
};

function GameContainer({ game, players, events, currentPlayer }: Props) {
  if (currentPlayer.state === PlayerState.JOINING) {
    return <Join />;
  }

  switch (game.state) {
    case GameState.LOBBY:
      return (
        <Lobby
          players={players}
          currentPlayer={currentPlayer}
          onStart={() => socket.emit("start_game")}
        />
      );
  }

  return (
    <ul>
      <li>{JSON.stringify(game)}</li>
      <li>{JSON.stringify(players)}</li>
      <li>{JSON.stringify(events)}</li>
      <li>{JSON.stringify(currentPlayer)}</li>
    </ul>
  );
}

export default GameContainer;
