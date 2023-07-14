import { useParams } from "react-router-dom";

function Game() {
    const {gameID} = useParams();
    return <h1>Game {gameID}</h1>
}

export default Game;
