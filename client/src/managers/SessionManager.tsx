import { ReactNode, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { socket } from "../socket";

type Props = {
  children: ReactNode;
  initializing: ReactNode;
};

function SessionManager({ children, initializing }: Props) {
  const navigate = useNavigate();
  const { game } = useParams();
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const session = localStorage.getItem("session");
    socket.auth = {
      session,
      game,
    };

    const handleSession = ({
      session,
      currentGame,
    }: {
      session: string;
      currentGame: string | null;
    }) => {
      localStorage.setItem("session", session);
      socket.auth = { session };

      if (currentGame != null) {
        navigate("/game/" + currentGame);
      } else {
        navigate("/");
      }

      setIsInitializing(false);
    };

    const handleDisconnect = () => {
      socket.connect();
    };

    const handleConnectionError = (e: Error) => {
      if (e.message === "invalid game id") {
        socket.auth = {
          session,
        };
        socket.connect();
      }
    };

    socket.on("session", handleSession);
    socket.on("disconnect", handleDisconnect);
    socket.on("connect_error", handleConnectionError);
    try {
      socket.connect();
    } catch (e) {
      debugger;
    }

    return () => {
      socket.off("session", handleSession);
      socket.off("disconnect", handleDisconnect);
      socket.off("connect_error", handleConnectionError);
      socket.disconnect();
    };
  }, []);

  return <>{isInitializing ? initializing : children}</>;
}

export default SessionManager;
