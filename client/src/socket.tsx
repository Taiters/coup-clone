import { io } from "socket.io-client";
import { useMessage } from "./managers/MessageManager";

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

export function useEventEmitter(): (event: string, ...args: any) => void {
  const { showMessage } = useMessage();
  return (event: string, ...args: any) =>
    socket
      .timeout(DEFAULT_TIMEOUT)
      .emit(event, ...args, (err: Error, response: SocketResponse) => {
        if (err != null) {
          showMessage("Error", "Request timed out");
          return;
        }

        if (response.status === "error") {
          showMessage("Error", response.error.message ?? "Something went wrong");
        }
      });
}
