import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";

import Button from "./ui/Button";
import HGroup from "./layout/HGroup";

import { socket } from "../socket";
import { useState } from "react";
import LinkButton from "./ui/LinkButton";
import { FaCircleQuestion } from "react-icons/fa6";
import Modal from "./ui/Modal";
import Help from "./Help";

function Home() {
  const [gameID, setGameID] = useState("");
  const [showHelp, setShowHelp] = useState(false);

  const onCreateGame = async () => {
    socket.emit("create_game");
  };

  const onJoinGame = async () => {
    socket.emit("join_game", gameID);
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
          />
          <Button label="Join" onClick={onJoinGame} />
        </HGroup>
        <LinkButton
          className="mt-28 mx-auto !block text-center"
          onClick={onCreateGame}
          label="Create a new game"
        />
        <LinkButton
          className="mt-4 mx-auto !block text-center"
          onClick={() => setShowHelp(true)}
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
