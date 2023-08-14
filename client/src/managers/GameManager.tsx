import { ReactNode, useEffect, useState } from "react";
import { Game, GameEvent, Player } from "../types";
import { socket } from "../socket";
import { useOutletContext } from "react-router-dom";
import { ActiveSession } from "./SessionManager";

type Props = {
  initializing: ReactNode;
  children: ({
    game,
    players,
    events,
    currentPlayer,
  }: {
    game: Game;
    players: Player[];
    events: GameEvent[];
    currentPlayer: Player;
  }) => ReactNode;
};

function GameManager({ initializing, children }: Props) {
  const session = useOutletContext<ActiveSession>();
  const [game, setGame] = useState<Game | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [events, setEvents] = useState<GameEvent[]>([]);

  const currentPlayer = players.find((p) => p.id == session.playerID);

  useEffect(() => {
    socket.emit("initialize_game");
  }, []);

  useEffect(() => {
    const handleGame = ({
      game,
      players,
      events,
    }: {
      game: Game;
      players: Player[];
      events: GameEvent[];
    }) => {
      setGame(game);
      setPlayers(players);
      setEvents(events);
    };

    // socket.on('update_players', handlePlayersUpdate);
    socket.on("game", handleGame);
    return () => {
      // socket.off('update_players', handlePlayersUpdate);
      socket.off("game", handleGame);
    };
  }, [setGame, setPlayers, setEvents]);

  if (game == null || currentPlayer == null) {
    return <>{initializing}</>;
  }

  return <>{children({ game, players, events, currentPlayer })}</>;
}

export default GameManager;
