import { ReactNode, useEffect, useState } from "react";
import { Game, GameEvent, Player } from "../types";
import { socket } from "../socket";

type Props = {
    render: (game: Game | null, players: Player[], events: GameEvent[], currentPlayer: Player | null) => ReactNode,
}

function GameManager({render}: Props) {
    const [game, setGame] = useState<Game | null>(null);
    const [players, setPlayers] = useState<Player[]>([]);
    const [events, setEvents] = useState<GameEvent[]>([]);
    const [currentPlayer, setCurrentPlayer] = useState<Player | null>(null);

    useEffect(() => {
        socket.emit('initialize_game')
    }, []);

    useEffect(() => {
        const handleGame = ({
                game,
                players,
                events,
                currentPlayer,
            }: {
                game: Game,
                players: Player[],
                events: GameEvent[],
                currentPlayer: Player
            }) => {
                setGame(game);
                setPlayers(players);
                setEvents(events);
                setCurrentPlayer(currentPlayer);
            };


        // socket.on('update_players', handlePlayersUpdate);
        socket.on('game', handleGame);
        return () => {
            // socket.off('update_players', handlePlayersUpdate);
            socket.off('game', handleGame);
        }
    }, [setPlayers, setCurrentPlayer])

    return render(game, players, events, currentPlayer);
}

export default GameManager;