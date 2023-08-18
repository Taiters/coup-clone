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
  STEAL,
  EXCHANGE,
  ASSASSINATE,
  COUP,
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
  turnStateModified: Date | null;
  turnStateDeadline: Date | null;
};

export type GameEvent = {
  id: number;
  timestamp: number;
  actor: Player;
  message: string;
};
