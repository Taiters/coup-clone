import { ReactNode, useEffect, useState } from "react";
import { Game, GameEvent, Player, PlayerInfluence } from "../types";
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
  const [hand, setHand] = useState<PlayerInfluence[]>([]);

  useEffect(() => {
    socket.emit("initialize_game");
  }, []);

  useEffect(() => {
    const handleAll = ({
      game,
      players,
      events,
      hand,
    }: {
      game: Game;
      players: Player[];
      events: GameEvent[];
      hand: PlayerInfluence[];
    }) => {
      setGame(game);
      setPlayers(players);
      setEvents(events);
      setHand(hand);
    };

    const handleGame = (game: Game) => {
      setGame(game);
    };

    const handlePlayers = (players: Player[]) => {
      setPlayers(players);
    };

    const handleEvents = (events: GameEvent[]) => {
      setEvents(events);
    };

    socket.on("game:all", handleAll);
    socket.on("game:game", handleGame);
    socket.on("game:players", handlePlayers);
    socket.on("game:events", handleEvents);

    return () => {
      socket.off("game", handleAll);
      socket.off("game:game", handleGame);
      socket.off("game:players", handlePlayers);
      socket.off("game:events", handleEvents);
    };
  }, [setGame, setPlayers, setEvents, setHand]);

  players.forEach((p) => (p.isCurrentTurn = p.id === game?.playerTurnID));
  const currentPlayer = players.find((p) => p.id === session.playerID);

  if (game == null || currentPlayer == null) {
    return <>{initializing}</>;
  }

  currentPlayer.influence = hand;
  return <>{children({ game, players, events, currentPlayer })}</>;
}

export default GameManager;
