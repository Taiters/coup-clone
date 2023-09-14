import { useParams } from "react-router-dom";
import Button from "./ui/Button";
import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";
import VGroup from "./layout/VGroup";
import { useState } from "react";
import { useEventEmitter } from "../socket";
import LinkButton from "./ui/LinkButton";

function Join() {
  const { game } = useParams();
  const [name, setName] = useState("");
  const emitEvent = useEventEmitter();

  const onContinue = () => emitEvent("set_name", name);
  const onLeave = () => emitEvent("leave_game");

  return (
    <Container>
      <PageTitle heading="Joining" subheading={`Game: ${game}`} />
      <VGroup>
        <TextInput
          value={name}
          onChange={setName}
          placeholder="Enter your name..."
        />
        <Button label="Continue" onClick={onContinue} />
        <LinkButton
          className="text-center mt-8"
          onClick={onLeave}
          label="Leave game"
        />
      </VGroup>
    </Container>
  );
}

export default Join;
