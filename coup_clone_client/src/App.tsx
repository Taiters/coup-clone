import {FaSpinner} from 'react-icons/fa6';
import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { socket } from "./socket";
import styles from "./App.module.css";


function App() {
    const navigate = useNavigate();
    const [sessionInitiated, setSessionInitiated] = useState(false);
    useEffect(() => {
        const sessionID = localStorage.getItem("sessionID");
        if (sessionID != null) {
            socket.auth = {sessionID};
        }

        const handleSession = (({
            sessionID,
            currentGameID
        }: {
            sessionID: string,
            currentGameID: string | null
        }) => {
            localStorage.setItem('sessionID', sessionID);
            socket.auth = {sessionID};

            if (currentGameID != null) {
                navigate("/game/" + currentGameID);
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