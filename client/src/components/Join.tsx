import { useParams } from "react-router-dom";
import Button from "./ui/Button";
import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";
import VGroup from "./layout/VGroup";
import React, { useState } from "react";
import { useEventEmitter } from "../socket";
import LinkButton from "./ui/LinkButton";

function Join() {
  const { game } = useParams();
  const [name, setName] = useState("");
  const [emitSetName, isSetNameInFlight] = useEventEmitter("set_name");
  const [emitLeaveGame, isLeaveGameInFlight] = useEventEmitter("leave_game");

  const onContinue = (e: React.FormEvent) => {
    e.preventDefault();
    emitSetName(name);
  };

  const onLeave = () => emitLeaveGame();

  return (
    <Container>
      <PageTitle heading="Joining" subheading={`Game: ${game}`} />
      <form onSubmit={onContinue}>
        <VGroup>
          <TextInput
            value={name}
            onChange={setName}
            placeholder="Enter your name..."
          />
          <Button label="Continue" type="submit" pending={isSetNameInFlight} />
          <LinkButton
            className="text-center mt-8"
            onClick={onLeave}
            pending={isLeaveGameInFlight}
            label="Leave game"
          />
        </VGroup>
      </form>
    </Container>
  );
}

export default Join;
