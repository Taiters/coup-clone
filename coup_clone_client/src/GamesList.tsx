import { useEffect, useState } from "react";

function GamesList() {
    const [games, setGames] = useState<string[] | null>(null);

    useEffect(() => {
        fetch('/games')
            .then(response => response.json().then(data => setGames(data.games)))
            .catch(e => {throw e;})
    }, []);

    return games == null ? (<p>Loading...</p>) : (<ul>{games.map(game => <li key={game}>{game}</li>)}</ul>);
}

export default GamesList;
