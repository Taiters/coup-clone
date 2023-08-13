export enum PlayerInfluence {
    UNKNOWN,
    AMBASSADOR,
    ASSASSIN,
    CAPTAIN,
    DUKE,
    CONTESSA,
}

export enum GameState {
    LOBBY,
    RUNNING,
}

export enum Action {
    INCOME,
    FOREIGN_AID,
    TAX,
    EXCHANGE,
    ASSASSINATE,
    COUP,
    STEAL,
    CHALLENGE,
    BLOCK,
}

export enum Outcome {
    PENDING,
    SUCCESS,
    FAIL,
}

export enum PlayerState {
    JOINING,
    JOINED,
}

export type PlayerID = string;
export type Player = {
    id: PlayerID,
    name: string,
    state: PlayerState,
    coins: number,
    influence: PlayerInfluence[],
    host: boolean,
}

export type GameID = string;
export type Game = {
    id: GameID,
    state: GameState,
    currentPlayerTurn: Player | null,
}

export type GameEventID = string;
export type GameEvent = {
    id: GameEventID,
    timestamp: number,
    actor: Player,
    target: Player | null,
    action: Action,
    response: GameEvent | null,
    outcome: Outcome,
    targetRevealed: PlayerInfluence | null,
    coinsReceived: number | null,
    coinsSpent: number | null,
}
