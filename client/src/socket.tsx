import { io } from "socket.io-client";
import { useMessage } from "./managers/MessageManager";
import { useCallback, useState } from "react";

const DEFAULT_TIMEOUT = 5000;

type SocketResponse =
  | {
      status: "success";
    }
  | {
      status: "error";
      error: {
        type: string;
        message: string | null;
      };
    };

export const socket = io(process.env.REACT_APP_SOCKET_ADDR ?? "", {
  autoConnect: false,
});

export function useEventEmitter(
  event: string,
): [(...args: any) => void, boolean] {
  const { showMessage } = useMessage();
  const [isInFlight, setIsInFlight] = useState(false);
  const emitEvent = useCallback(
    (...args: any) => {
      setIsInFlight(true);
      socket
        .timeout(DEFAULT_TIMEOUT)
        .emit(event, ...args, (err: Error, response: SocketResponse) => {
          setIsInFlight(false);
          if (err != null) {
            showMessage("Error", "Request timed out");
            return;
          }

          if (response.status === "error") {
            showMessage(
              "Error",
              response.error.message ?? "Something went wrong",
            );
          }
        });
    },
    [event, showMessage],
  );

  return [emitEvent, isInFlight];
}
