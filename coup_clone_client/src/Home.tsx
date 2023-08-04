import { useSubmit } from "react-router-dom";
import styles from "./Home.module.css";
import Button, { ButtonStyle } from "./Button";
import TurnActions from "./TurnActions";
import Flex from "./Flex";

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
        <Flex>
            <TurnActions />
            <Flex direction="column" grow={1}>
                <TurnActions />
                <TurnActions />
            </Flex>
            <TurnActions />
            <Flex direction="column" grow={1}>
                <TurnActions />
                <TurnActions />
                <TurnActions />
                <TurnActions />
            </Flex>
            <TurnActions />
        </Flex>
    );
}

export default Home;
