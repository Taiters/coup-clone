import Container from "./Container";
import PageTitle from "./PageTitle";
import TextInput from "./TextInput";

import Button from "./Button";
import HGroup from "./HGroup";

import styles from "./Home.module.css";
import { socket } from "./socket";
import { useState } from "react";
import { useNavigate } from "react-router-dom";


function Home() {
    const [gameID, setGameID] = useState('');
    const navigate = useNavigate();

    const onCreateGame = async () => {
        socket.connect();
        const createdGameID = await socket.timeout(5000).emitWithAck('create_game');
        navigate('/game/' + createdGameID);
    }

    const onJoinGame = async () => {
        socket.connect();
        const joinedGameID = await socket.timeout(5000).emitWithAck('join_game', gameID);
        navigate('/game/' + joinedGameID);
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
