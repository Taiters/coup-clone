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

export enum TurnState {
  START,
  ATTEMPTED,
  BLOCKED,
  CHALLENGED,
  BLOCK_CHALLENGED,
  REVEALING,
  TARGET_REVEALING,
}

export enum TurnAction {
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
  influenceA: PlayerInfluence;
  influenceB: PlayerInfluence;
  host: boolean;
  isCurrentTurn: boolean;
  hand: {
    influenceA: PlayerInfluence;
    influenceB: PlayerInfluence;
  } | null;
};

export type Game = {
  id: string;
  state: GameState;
  currentTurn: Player;
  turnState: TurnState;
  turnAction: TurnAction;
  turnStateModified: Date | null;
  turnStateDeadline: Date | null;
  turnTarget: Player | null;
};

export type GameEvent = {
  id: number;
  timestamp: number;
  actor: Player;
  message: string;
};
