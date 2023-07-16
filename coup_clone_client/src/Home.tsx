import { useSubmit } from "react-router-dom";

function Home() {
    const submit = useSubmit();
    const createGame = () => {
        submit({}, {
            method: "post",
            action: "/"
        });
    }
    return (
        <div>
            <h1>Coup Clone</h1>
            <div>
                <button onClick={createGame}>Create Game</button>
            </div>
            <div>
                <input type="text" />
                <button>Join</button>
            </div>
        </div>
    );
}

export default Home;
