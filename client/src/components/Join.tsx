import { useParams } from "react-router-dom";
import Button from "./ui/Button";
import Container from "./layout/Container";
import PageTitle from "./ui/PageTitle";
import TextInput from "./ui/TextInput";
import VGroup from "./layout/VGroup";
import { useState } from "react";
import { socket } from "../socket";
import LeaveButton from "./LeaveButton";

function Join() {
  const { gameID } = useParams();
  const [name, setName] = useState("");

  const onContinue = () => {
    console.log("SET NAME");
    socket.emit("set_name", name);
  };

  return (
    <Container>
      <PageTitle heading="Joining" subheading={gameID} />
      <VGroup>
        <TextInput
          value={name}
          onChange={setName}
          placeholder="Enter your name..."
        />
        <Button label="Continue" onClick={onContinue} />
        <LeaveButton />
      </VGroup>
    </Container>
  );
}

export default Join;
