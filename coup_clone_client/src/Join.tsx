import { useParams } from "react-router-dom";
import Button from "./Button";
import Container from "./Container";
import PageTitle from "./PageTitle";
import TextInput from "./TextInput";
import VGroup from "./VGroup";
import { useState } from "react";
import { socket } from "./socket";

function Join() {
    const {gameID} = useParams();
    const [name, setName] = useState("");

    const onContinue = () => {
        socket.emit("set_name", name);
    }

    return (
        <Container>
            <PageTitle heading="Joining" subheading={gameID} />
            <VGroup>
                <TextInput 
                    value={name}
                    onChange={setName}
                    placeholder="Enter your name..." />
                <Button label="Continue" onClick={onContinue} />
            </VGroup>
        </Container>
    );
}

export default Join;