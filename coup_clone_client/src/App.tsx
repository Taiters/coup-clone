import {FaSpinner} from 'react-icons/fa6';
import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { socket } from "./socket";
import styles from "./App.module.css";


function App() {
    const navigate = useNavigate();
    const [sessionInitiated, setSessionInitiated] = useState(false);
    useEffect(() => {
        const session = localStorage.getItem("session");
        if (session != null) {
            socket.auth = {session};
        }

        const handleSession = (({
            session,
            currentGame
        }: {
            session: string,
            currentGame: string | null
        }) => {
            localStorage.setItem('session', session);
            socket.auth = {session};

            if (currentGame != null) {
                navigate("/game/" + currentGame);
            } else {
                navigate("/");
            }

            setSessionInitiated(true);
        });

        socket.on('session', handleSession);
        socket.connect();

        return () => {
            socket.off('session', handleSession);
            socket.disconnect();
        }
    }, []);

    return sessionInitiated ? <Outlet /> : (
        <div className={styles.container}>
            <FaSpinner className={styles.spinner} />
            <h1>Connecting</h1>
        </div>
    );
}

export default App;