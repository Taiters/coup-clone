import { useSubmit } from "react-router-dom";
import styles from "./Home.module.css";
import Button, { ButtonStyle } from "./Button";
import TurnActions from "./TurnActions";
import Flex from "./Flex";
import Card from "./Card";
import PlayerList from "./PlayerList";
import GameLog from "./GameLog";

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
            <Card heading="Game">
                <Flex direction="column">
                    <PlayerList />
                    <GameLog />
                </Flex>
            </Card>
            <Card heading="Your turn" subheading="What's your next move?">
                <TurnActions />
            </Card>
        </Flex>
    );
}

export default Home;
