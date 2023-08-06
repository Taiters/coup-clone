import { FaCopy } from "react-icons/fa6";

import Button from "./Button";
import Container from "./Container";
import PageTitle from "./PageTitle";
import TextInput from "./TextInput";
import VGroup from "./VGroup";

function Join() {
    return (
        <Container>
            <PageTitle heading="Join" subheading={<>Game: <u>123ABC</u> <FaCopy /></>} />
            <VGroup>
                <TextInput placeholder="Enter your name..." />
                <Button label="Continue" />
            </VGroup>
        </Container>
    );
}

export default Join;