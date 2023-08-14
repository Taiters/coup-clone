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

function SessionManager({ children, initializing }: Props) {
  const navigate = useNavigate();
  const { game } = useParams();
  const [activeSession, setActiveSession] = useState<ActiveSession | null>(
    null,
  );

  useEffect(() => {
    const handleSession = ({session, gameID}: {session: ActiveSession, gameID: string}) => {
      console.log('session');
      console.log({session, gameID});
      localStorage.setItem("session", session.id);
      socket.auth = { ...socket.auth, session: session.id };

      if (gameID != null) {
        navigate("/game/" + gameID);
      } else {
        navigate("/");
      }

      setActiveSession(session);
    };

    socket.on("session", handleSession);

    return () => {
      socket.off("session", handleSession);
    };
  }, [navigate, setActiveSession]);

  useEffect(() => {
    const session = localStorage.getItem("session");
    socket.auth = {
      session,
      game,
    };

    const handleConnectionError = (e: Error) => {
      console.log('connection error');
      console.log(e);
      if (e.message === "invalid game id") {
        socket.auth = {
          session,
        };
        socket.connect();
      }
    };

    const handleDisconnect = () => {
      console.log('disconnect');
      socket.connect();
    };

    socket.on("connect_error", handleConnectionError);
    socket.on("disconnect", handleDisconnect);
    socket.connect();

    return () => {
      socket.off("connect_error", handleConnectionError);
      socket.off("disconnect", handleDisconnect);
      console.log('disconnecting');
      socket.disconnect();
    };
  }, [game]);

  if (activeSession == null) {
    return <>{initializing}</>;
  }

  return <>{children(activeSession)}</>;
}

export default SessionManager;
