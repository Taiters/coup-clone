import {FaSpinner} from 'react-icons/fa6';
import { Outlet } from "react-router-dom";

import styles from "./App.module.css";
import SessionManager from '../managers/SessionManager';


function App() {
    return (
        <SessionManager 
            initializing={
            <div className={styles.container}>
                <FaSpinner className="spinner" />
                <h1>Connecting</h1>
            </div>
            }>
            <Outlet />
        </SessionManager>
    );
}

export default App;