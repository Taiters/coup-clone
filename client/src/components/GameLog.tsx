import GameLogEvent from "./GameLogEvent";
import { GameEvent } from "../types";
import { useEffect, useRef } from "react";

type Props = {
  events: GameEvent[];
};

function GameLog({ events }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior: 'smooth'});
  }, [events]);
  return (
    <>
    <div>
      {events.map((e) => (
        <GameLogEvent key={e.id} event={e} />
      ))}
    </div>
    <div ref={bottomRef} />
    </>
  );
}

export default GameLog;
