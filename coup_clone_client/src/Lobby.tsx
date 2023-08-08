import Button from "./Button";
import Container from "./Container";
import LobbyPlayer from "./LobbyPlayer";
import PageTitle from "./PageTitle";
import VGroup from "./VGroup";
import styles from "./Lobby.module.css";

type Props = {
    onStart: () => void,
}

function Lobby({onStart}: Props) {
    return (
        <Container>
            <PageTitle heading="Lobby" subheading="Code: 123ABC" />
            <VGroup className={styles.players}>
                <LobbyPlayer name="Danny boy" />
                <LobbyPlayer name="Snejy Meche" />
                <LobbyPlayer name="Walter White" />
                <LobbyPlayer name="Jesse Pinkman" />
                <LobbyPlayer />
                <LobbyPlayer />
            </VGroup>
            <VGroup>
                <Button label="Start" onClick={onStart} />
            </VGroup>

        </Container>
    )
}

export default Lobby;