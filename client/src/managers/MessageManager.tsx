import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import Message from "../components/ui/Message";
import { socket } from "../socket";

type Props = {
  children: ReactNode;
};

type MessageContextType = {
  showMessage: (title: string, message: string) => void;
};

const MessageContext = createContext<MessageContextType>({
  showMessage: () => {},
});

export const useMessage = () => {
  return useContext(MessageContext);
};

function MessageManager({ children }: Props) {
  const [message, setMessage] = useState<{
    title: string;
    message: string;
  } | null>(null);

  const showMessage = useCallback(
    (title: string, message: string) => {
      setMessage({ title, message });
    },
    [setMessage],
  );

  useEffect(() => {
    if (message == null) {
      return;
    }

    const timeout = setTimeout(() => setMessage(null), 5000);

    return () => {
      clearTimeout(timeout);
    };
  }, [message, setMessage]);

  useEffect(() => {
    const handleErrorMsg = (message: { title: string; message: string }) => {
      setMessage(message);
    };
    socket.on("error_msg", handleErrorMsg);

    return () => {
      socket.off("error_msg", handleErrorMsg);
    };
  }, [setMessage]);

  return (
    <>
      <MessageContext.Provider value={{ showMessage }}>
        {children}
      </MessageContext.Provider>
      {message && <Message title={message.title} message={message.message} />}
    </>
  );
}

export default MessageManager;
