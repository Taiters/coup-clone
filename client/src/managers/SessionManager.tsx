import { ReactNode, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { socket } from "../socket";

type Props = {
  children: (session: ActiveSession) => ReactNode;
  initializing: ReactNode;
};

export type ActiveSession = {
  id: string;
  playerID: number;
};

type SessionNotification = {
  session: {
    id: string;
    player_id: number;
  };
  game_id: string;
};

function SessionManager({ children, initializing }: Props) {
  const navigate = useNavigate();
  const { game } = useParams();
  const [session, setSession] = useState<SessionNotification | null>(null);

  useEffect(() => {
    const handleSession = (sessionNotification: SessionNotification) => {
      const { session, game_id } = sessionNotification;
      localStorage.setItem("session", session.id);
      socket.auth = { ...socket.auth, session: session.id };

      if (game_id != null) {
        navigate("/game/" + game_id);
      } else {
        navigate("/");
      }

      setSession(sessionNotification);
    };

    socket.on("session", handleSession);

    return () => {
      socket.off("session", handleSession);
    };
  }, [navigate, setSession]);

  useEffect(() => {
    const session = localStorage.getItem("session");
    socket.auth = {
      session,
      game,
    };

    const handleConnectionError = (e: Error) => {
      if (e.message === "invalid game id") {
        socket.auth = {
          session,
        };
        socket.connect();
      }
    };

    const handleDisconnect = () => {
      socket.connect();
    };

    socket.on("connect_error", handleConnectionError);
    socket.on("disconnect", handleDisconnect);
    socket.connect();

    return () => {
      socket.off("connect_error", handleConnectionError);
      socket.off("disconnect", handleDisconnect);
    };
  }, [game]);

  if (session == null) {
    return <>{initializing}</>;
  }

  return (
    <>
      {children({
        id: session.session.id,
        playerID: session.session.player_id,
      })}
    </>
  );
}

export default SessionManager;
