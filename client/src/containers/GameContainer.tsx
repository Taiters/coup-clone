import { Game, GameEvent, Player } from "../types";

type Props = {
    game: Game | null,
    players: Player[], 
    events: GameEvent[], 
    currentPlayer: Player | null
}

function GameContainer({game, players, events, currentPlayer}: Props) {
    return <ul>
        <li>{JSON.stringify(game)}</li>
        <li>{JSON.stringify(players)}</li>
        <li>{JSON.stringify(events)}</li>
        <li>{JSON.stringify(currentPlayer)}</li>
    </ul>
}

export default GameContainer;