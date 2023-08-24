import styles from "./GameLogEvent.module.css";
import { GameEvent } from "../types";

type Props = {
  event: GameEvent;
};

function EventLine({ event }: { event: GameEvent }) {
  return <span>{event.message}</span>;
}

function GameLogEventInner({ event }: { event: GameEvent }) {
  return (
    <div>
      <p className="p-0 m-0">
        <EventLine event={event} />
      </p>
    </div>
  );
}

function GameLogEvent({ event }: Props) {
  return (
    <div className={styles.container}>
      <GameLogEventInner event={event} />
    </div>
  );
}

export default GameLogEvent;
