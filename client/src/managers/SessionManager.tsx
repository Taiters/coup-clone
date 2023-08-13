import { ReactNode, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { socket } from "../socket";

type Props = {
  children: ReactNode;
  initializing: ReactNode;
};

function SessionManager({ children, initializing }: Props) {
  const navigate = useNavigate();
  const [isInitializing, setIsInitializing] = useState(true);
  useEffect(() => {
    const session = localStorage.getItem("session");
    if (session != null) {
      socket.auth = { session };
    }

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

    socket.on("session", handleSession);
    socket.connect();

    return () => {
      socket.off("session", handleSession);
      socket.disconnect();
    };
  }, []);

  return <>{isInitializing ? initializing : children}</>;
}

export default SessionManager;
