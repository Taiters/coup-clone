import Container from "./Container";
import PageTitle from "./PageTitle";
import TextInput from "./TextInput";

import Button from "./Button";
import HGroup from "./HGroup";

import styles from "./Home.module.css";
import { Link } from "react-router-dom";

function Home() {
    return (
        <Container>
            <PageTitle heading="Coup" subheading="Another online Coup clone" />
            <HGroup>
                <TextInput placeholder="Enter game code..." />
                <Button label="Join" />
            </HGroup>
            <Link to="join" className={styles.create}>Create a new game</Link>
        </Container>
    );
}

export default Home;
