import { ReactNode, useEffect, useState } from "react";
import {
  Game,
  GameEvent,
  GameState,
  Player,
  PlayerInfluence,
  PlayerState,
} from "../types";
import { socket } from "../socket";
import { useOutletContext } from "react-router-dom";
import { ActiveSession } from "./SessionManager";
import { nullthrows } from "../utils";

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

type GameNotification = {
  id: string;
  state: GameState;
  player_turn_id: number | null;
};

type PlayerNotification = {
  id: number;
  name: string | null;
  state: PlayerState;
  coins: number;
  influence: PlayerInfluence[];
  host: boolean;
};

type EventNotification = {
  id: number;
  timestamp: number;
  actor_id: number;
  message: string;
};

function GameManager({ initializing, children }: Props) {
  const session = useOutletContext<ActiveSession>();
  const [game, setGame] = useState<GameNotification | null>(null);
  const [players, setPlayers] = useState<PlayerNotification[]>([]);
  const [events, setEvents] = useState<EventNotification[]>([]);
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
      game: GameNotification;
      players: PlayerNotification[];
      events: EventNotification[];
      hand: PlayerInfluence[];
    }) => {
      setGame(game);
      setPlayers(players);
      setEvents(events);
      setHand(hand);
    };

    const handleGame = (game: GameNotification) => {
      setGame(game);
    };

    const handlePlayers = (players: PlayerNotification[]) => {
      setPlayers(players);
    };

    const handleEvents = (events: EventNotification[]) => {
      setEvents(events);
    };

    socket.on("game:all", handleAll);
    socket.on("game:game", handleGame);
    socket.on("game:players", handlePlayers);
    socket.on("game:events", handleEvents);

    return () => {
      socket.off("game:all", handleAll);
      socket.off("game:game", handleGame);
      socket.off("game:players", handlePlayers);
      socket.off("game:events", handleEvents);
    };
  }, [setGame, setPlayers, setEvents, setHand]);

  const gamePlayers = players.map((p) => ({
    id: p.id,
    name: p.name ?? "",
    state: p.state,
    coins: p.coins,
    influence: p.influence,
    host: p.host,
    isCurrentTurn: p.id === game?.player_turn_id,
  }));
  const currentTurn = gamePlayers.find((p) => p.id === game?.player_turn_id);
  const currentPlayer = gamePlayers.find((p) => p.id === session.playerID);

  const gameEvents = events.map((e) => ({
    id: e.id,
    timestamp: e.timestamp,
    actor: nullthrows(gamePlayers.find((p) => p.id === e.actor_id)),
    message: e.message,
  }));

  if (game == null || currentPlayer == null || currentTurn == null) {
    return <>{initializing}</>;
  }

  currentPlayer.influence = hand;
  return (
    <>
      {children({
        game: {
          id: game.id,
          state: game.state,
          currentTurn,
        },
        players: gamePlayers,
        events: gameEvents,
        currentPlayer,
      })}
    </>
  );
}

export default GameManager;
