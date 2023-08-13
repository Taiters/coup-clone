import GameLogEvent from "./GameLogEvent";
import { Action, GameEvent, Outcome, PlayerInfluence } from "./types";

function GameLog() {
    const events: GameEvent[] = [
        // {
        //     id: "1",
        //     timestamp: 0,
        //     actor: {id: "1", name: "Danny boy", coins: 0, influence: []},
        //     target: null,
        //     targetRevealed: null,
        //     coinsReceived: 1,
        //     coinsSpent: null,
        //     action: Action.INCOME,
        //     response: null,
        //     outcome: Outcome.SUCCESS,
        // },
        // {
        //     id: "2",
        //     timestamp: 1,
        //     actor: {id: "2", name: "Snejy Meche", coins: 0, influence: []},
        //     target: {id: "1", name: "Danny boy", coins: 0, influence: []},
        //     targetRevealed: null,
        //     coinsReceived: null,
        //     coinsSpent: null,
        //     action: Action.STEAL,
        //     outcome: Outcome.PENDING,
        //     response: {
        //         id: "3",
        //         timestamp: 2,
        //         actor: {id: "1", name: "Danny boy", coins: 0, influence: []},
        //         target: {id: "2", name: "Snejy Meche", coins: 0, influence: []},
        //         action: Action.BLOCK,
        //         outcome: Outcome.PENDING,
        //         targetRevealed: null,
        //         coinsReceived: null,
        //         coinsSpent: null,
        //         response: {
        //             id: "4",
        //             timestamp: 3,
        //             target: {id: "1", name: "Danny boy", coins: 0, influence: []},
        //             targetRevealed: PlayerInfluence.DUKE,
        //             actor: {id: "2", name: "Snejy Meche", coins: 0, influence: []},
        //             action: Action.CHALLENGE,
        //             response: null,
        //             outcome: Outcome.SUCCESS,
        //             coinsReceived: null,
        //             coinsSpent: null,
        //         },
        //     },
        // },
        // {
        //     id: "1",
        //     timestamp: 0,
        //     actor: {id: "1", name: "Snejy Meche", coins: 0, influence: []},
        //     target: {id: "1", name: "Danny boy", coins: 0, influence: []},
        //     targetRevealed: PlayerInfluence.ASSASSIN,
        //     coinsReceived: 0,
        //     coinsSpent: 3,
        //     action: Action.ASSASSINATE,
        //     response: null,
        //     outcome: Outcome.SUCCESS,
        // },
    ]
    return (
        <div>
            {events.map(e => <GameLogEvent key={e.id} event={e} />)}
        </div>
    );
}

export default GameLog;