import { useEffect, useReducer } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Game, GameEvent, Player } from "./types";
import { socket } from "./socket";

export type AppState = {
    game: Game | null,
    players: Player[],
    events: GameEvent[],
    currentPlayer: Player | null,
}

type DispatchAction = 
{
    type: "init",
    game: Game,
    players: Player[],
    events: GameEvent[],
    currentPlayer: Player,
} | {
    type: "players_updated",
    players: Player[],
}

function App() {
    const navigate = useNavigate();
    const [appState, dispatch] = useReducer((currentState: AppState, action: DispatchAction) => {
        switch (action.type) {
            case "init":
                navigate("/game/"+action.game.id);
                return {
                    game: action.game,
                    players: action.players,
                    events: action.events,
                    currentPlayer: action.currentPlayer,
                };
            case "players_updated":
                const currentPlayer = action.players.find(p => p.id === currentState.currentPlayer?.id);
                return {
                    ...currentState,
                    players: action.players,
                    currentPlayer: currentPlayer ?? null,
                }
        }
    }, {
        game: null,
        players: [],
        events: [],
        currentPlayer: null,
    });

    useEffect(() => {
        const handleWelcome = (data: any) => dispatch({
            type: "init",
            game: data.game,
            players: data.players,
            events: data.events,
            currentPlayer: data.currentPlayer,
        });

        const handlePlayersUpdated = (data: any) => dispatch({
            type: "players_updated",
            players: data.players,
        });

        socket.on('welcome', handleWelcome);
        socket.on('players_updated', handlePlayersUpdated)

        return () => {
            socket.off('welcome', handleWelcome);
            socket.off('players_updated', handlePlayersUpdated);
        }
    }, []);

    return (
        <Outlet context={appState} />
    );
}

export default App;