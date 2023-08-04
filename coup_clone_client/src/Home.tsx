import { useSubmit } from "react-router-dom";
import styles from "./Home.module.css";

function Home() {
    const submit = useSubmit();
    const createGame = () => {
        submit({}, {
            method: "post",
            action: "/"
        });
    }
    return (
        // <div>
        //     <h1>Coup Clone</h1>
        //     <div>
        //         <button onClick={createGame}>Create Game</button>
        //     </div>
        //     <div>
        //         <input type="text" />
        //         <button>Join</button>
        //     </div>
        // </div>
        <menu className={styles.actions}>
            <li>
                <button>Income</button>
            </li>
            <li>
                <button>Foreign Aid</button>
            </li>
            <li>
                <button>Tax</button>
            </li>
            <li>
                <button>Steal</button>
            </li>
            <li>
                <button>Assasinate</button>
            </li>
            <li>
                <button>Exchnage</button>
            </li>
            <li>
                <button>Coup</button>
            </li>
        </menu>
    );
}

export default Home;
