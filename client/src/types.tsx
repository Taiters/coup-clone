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
  PENDING,
  READY,
}

export type Player = {
  id: number;
  name: string;
  state: PlayerState;
  coins: number;
  influence: PlayerInfluence[];
  host: boolean;
  isCurrentTurn: boolean;
};

export type Game = {
  id: string;
  state: GameState;
  currentTurn: Player;
};

export type GameEvent = {
  id: number;
  timestamp: number;
  actor: Player;
  message: string;
};
