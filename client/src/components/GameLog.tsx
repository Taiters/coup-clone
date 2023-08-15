import GameLogEvent from "./GameLogEvent";
import { GameEvent } from "../types";

type Props = {
  events: GameEvent[];
};

function GameLog({ events }: Props) {
  return (
    <div>
      {events.map((e) => (
        <GameLogEvent key={e.id} event={e} />
      ))}
    </div>
  );
}

export default GameLog;
