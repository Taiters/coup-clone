import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";

import Button from "./ui/Button";
import HGroup from "./layout/HGroup";

import { socket } from "../socket";
import { useState } from "react";
import LinkButton from "./ui/LinkButton";
import Modal from "./ui/Modal";
import Help from "./Help";
import { useMessage } from "../managers/MessageManager";

function Home() {
  const [gameID, setGameID] = useState("");
  const [showHelp, setShowHelp] = useState(false);
  const {showMessage} = useMessage();

  const onCreateGame = async () => {
    socket.timeout(5000).emit("create_game", (err: Error) => {
      if (err != null) {
        showMessage("Error", "Timed out when creating game")
      }
    });
  };

  const onJoinGame = async () => {
    socket.timeout(5000).emit("join_game", gameID, (err: Error) => {
      if (err != null) {
        showMessage("Error", "Timed out when joining game")
      }
    });
  };

  return (
    <>
      <Container>
        <PageTitle heading="Coup" subheading="Another online Coup clone" />
        <HGroup>
          <TextInput
            value={gameID}
            onChange={setGameID}
            placeholder="Enter game code..."
            validate={(value) => value.length !== 6 ? "Game code should be 6 characters" : null}
          />
          <Button label="Join" onClick={onJoinGame} disabled={gameID.length !== 6} />
        </HGroup>
        <LinkButton
          className="mt-28 mx-auto !block text-center"
          onClick={onCreateGame}
          label="Create a new game"
        />
        <LinkButton
          className="mt-4 mx-auto !block text-center"
          onClick={() => showMessage('hello', 'world')}
          label="How to play"
        />
      </Container>
      {showHelp && (
        <Modal heading="How to play" onClose={() => setShowHelp(false)}>
          <Help />
        </Modal>
      )}
    </>
  );
}

export default Home;
