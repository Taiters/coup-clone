import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";

import Button from "./ui/Button";
import HGroup from "./layout/HGroup";

import { socket } from "../socket";
import { useState } from "react";

function Home() {
  const [gameID, setGameID] = useState("");

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
        <a
          className="mt-28 block text-purple text-center"
          href="#"
          onClick={onCreateGame}
        >
          Create a new game
        </a>
      </Container>
    </>
  );
}

export default Home;
