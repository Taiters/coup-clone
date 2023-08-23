import { ReactNode, useEffect, useState } from "react";
import {
  Game,
  GameEvent,
  GameState,
  Player,
  PlayerInfluence,
  PlayerState,
  TurnAction,
  TurnState,
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
  turn_state: TurnState;
  turn_action: TurnAction;
  turn_state_modified: number | null;
  turn_state_deadline: number | null;
  turn_target: number | null;
  turn_challenger: number | null;
  turn_blocker: number | null;
  turn_block_challenger: number | null;
  winner: number | null;
};

type PlayerNotification = {
  id: number;
  name: string | null;
  state: PlayerState;
  coins: number;
  influence_a: PlayerInfluence;
  influence_b: PlayerInfluence;
  host: boolean;
};

type HandNotification = {
  influence_a: PlayerInfluence;
  influence_b: PlayerInfluence;
};

type EventNotification = {
  id: number;
  timestamp: number;
  message: string;
};

function GameManager({ initializing, children }: Props) {
  const session = useOutletContext<ActiveSession>();
  const [game, setGame] = useState<GameNotification | null>(null);
  const [players, setPlayers] = useState<PlayerNotification[]>([]);
  const [events, setEvents] = useState<EventNotification[]>([]);
  const [hand, setHand] = useState<HandNotification | null>(null);

  useEffect(() => {
    socket.emit("initialize_game");
  }, []);

  useEffect(() => {
    const handleGame = ({
      game,
      players,
      events,
    }: {
      game: GameNotification;
      players: PlayerNotification[];
      events: EventNotification[];
    }) => {
      setGame(game);
      setPlayers(players);
      setEvents(events);
    };

    const handleHand = (hand: HandNotification) => {
      setHand(hand);
    };

    socket.on("game", handleGame);
    socket.on("hand", handleHand);

    return () => {
      socket.off("game", handleGame);
      socket.off("hand", handleHand);
    };
  }, [setGame, setPlayers, setEvents, setHand]);

  const gamePlayers = players.map<Player>((p) => ({
    id: p.id,
    name: p.name ?? "",
    state: p.state,
    coins: p.coins,
    influenceA: p.influence_a,
    influenceB: p.influence_b,
    host: p.host,
    isCurrentTurn: p.id === game?.player_turn_id,
    hand: null,
  }));
  const currentTurn = gamePlayers.find((p) => p.id === game?.player_turn_id);
  const currentPlayer = gamePlayers.find((p) => p.id === session.playerID);

  const gameEvents = events.map((e) => ({
    id: e.id,
    timestamp: e.timestamp,
    message: e.message,
  }));

  if (
    game == null ||
    currentPlayer == null ||
    currentTurn == null ||
    hand == null
  ) {
    return <>{initializing}</>;
  }

  currentPlayer.hand = {
    influenceA: hand.influence_a,
    influenceB: hand.influence_b,
  };

  return (
    <>
      {children({
        game: {
          id: game.id,
          state: game.state,
          turnState: game.turn_state,
          turnAction: game.turn_action,
          turnStateModified:
            game.turn_state_modified != null
              ? new Date(nullthrows(game.turn_state_modified) * 1000)
              : null,
          turnStateDeadline:
            game.turn_state_deadline != null
              ? new Date(nullthrows(game.turn_state_deadline) * 1000)
              : null,
          turnTarget:
            gamePlayers.find((p) => p.id === game?.turn_target) ?? null,
          turnChallenger:
            gamePlayers.find((p) => p.id === game?.turn_challenger) ?? null,
          turnBlocker:
            gamePlayers.find((p) => p.id === game?.turn_blocker) ?? null,
          turnBlockChallenger:
            gamePlayers.find((p) => p.id === game?.turn_block_challenger) ??
            null,
          currentTurn,
          winner: gamePlayers.find((p) => p.id === game?.winner) ?? null,
        },
        players: gamePlayers,
        events: gameEvents,
        currentPlayer,
      })}
    </>
  );
}

export default GameManager;
