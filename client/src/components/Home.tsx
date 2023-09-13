import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";

import Button from "./ui/Button";
import HGroup from "./layout/HGroup";

import { useEventEmitter } from "../socket";
import { useState } from "react";
import LinkButton from "./ui/LinkButton";
import Modal from "./ui/Modal";
import Help from "./Help";

function Home() {
  const [gameID, setGameID] = useState("");
  const [showHelp, setShowHelp] = useState(false);
  const emitEvent = useEventEmitter();

  const onCreateGame = async () => emitEvent("create_game");
  const onJoinGame = async () => emitEvent("join_game", gameID);

  return (
    <>
      <Container>
        <PageTitle heading="Coup" subheading="Another online Coup clone" />
        <HGroup>
          <TextInput
            value={gameID}
            onChange={setGameID}
            placeholder="Enter game code..."
            validate={(value) =>
              value.length !== 6 ? "Game code should be 6 characters" : null
            }
          />
          <Button
            label="Join"
            onClick={onJoinGame}
            disabled={gameID.length !== 6}
          />
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
