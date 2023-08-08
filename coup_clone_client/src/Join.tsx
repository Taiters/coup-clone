import { useNavigate } from "react-router-dom";
import Button from "./Button";
import Container from "./Container";
import PageTitle from "./PageTitle";
import TextInput from "./TextInput";
import VGroup from "./VGroup";

function Join() {
    const navigate = useNavigate();
    return (
        <Container>
            <PageTitle heading="Joining" subheading="123ABC" />
            <VGroup>
                <TextInput placeholder="Enter your name..." />
                <Button label="Continue" onClick={() => navigate("/game")} />
            </VGroup>
        </Container>
    );
}

export default Join;