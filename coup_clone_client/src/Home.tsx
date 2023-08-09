import Container from "./Container";
import PageTitle from "./PageTitle";
import TextInput from "./TextInput";

import Button from "./Button";
import HGroup from "./HGroup";

import styles from "./Home.module.css";
import { socket } from "./socket";
import { useState } from "react";


function Home() {
    const [gameID, setGameID] = useState('');
    const onCreateGame = () => {
        socket.connect();
        socket.emit('create');
    }
    const onJoinGame = () => {
        socket.connect();
        socket.emit('join', {
            'game_id': gameID,
        })
    }

    return (
        <Container>
            <PageTitle heading="Coup" subheading="Another online Coup clone" />
            <HGroup>
                <TextInput value={gameID} onChange={setGameID} placeholder="Enter game code..." />
                <Button label="Join" onClick={onJoinGame} />
            </HGroup>
            <a className={styles.create} href="#" onClick={onCreateGame}>Create a new game</a>
        </Container>
    );
}

export default Home;
