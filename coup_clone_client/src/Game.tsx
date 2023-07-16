import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { socket } from "./socket";


function Game() {
    const { gameID } = useParams();
    const [connected, setConnected] = useState(socket.connected);
    const [responses, setResponses] = useState<string[]>([]);
    const [msg, setMsg] = useState<string>('');
    const [name, setName] = useState<string>('');
    const [joined, setJoined] = useState(false);


    const sendMessage = () => {
        socket.send({
            game_id: gameID,
            msg,
            name,
        });
        setMsg('');
    }

    const sendJoin = () => {
        socket.emit('join', {
            name,
            game_id: gameID,
        });
        setJoined(true);
    }

    useEffect(() => {
        const onConnected = () => setConnected(true);
        const onDisconnected = () => setConnected(false);
        const onMessage = (message: string) => setResponses((responses) => [...responses, message]);

        socket.on('connect', onConnected);
        socket.on('disconnect', onDisconnected);
        socket.on('message', onMessage);

        socket.connect();

        return () => { 
            socket.off('connect', onConnected);
            socket.off('disconnect', onDisconnected);
            socket.off('message', onMessage);

            socket.disconnect()
        }
    }, []);

    return (
        <div>
            <h1>Game {gameID}</h1>
            <p>Connected: {connected ? 'YES' : 'NO'}</p>
            {connected && (
                joined ? (
                <div>
                <input type="text" value={msg} onChange={(e) => setMsg(e.target.value)} /> <button onClick={sendMessage}>Send</button>
                <ul>
                    {responses.map((response, i) => <li key={i}>{response}</li>)}
                </ul>
                </div>
                ) : (
                <div>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} /> <button onClick={sendJoin}>Join</button>
                </div>
                )
            )}
        </div>
    );
}

export default Game;
