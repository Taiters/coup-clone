import styles from "./GameLogEvent.module.css";
import { GameEvent } from "../types";

type Props = {
  event: GameEvent;
};

// const actionNameText = (action: Action): string => {
//   switch (action) {
//     case Action.INCOME:
//       return "Income";
//     case Action.FOREIGN_AID:
//       return "Foreign Aid";
//     case Action.TAX:
//       return "Tax";
//     case Action.EXCHANGE:
//       return "Exchange";
//     case Action.ASSASSINATE:
//       return "Assasinate";
//     case Action.COUP:
//       return "Coup";
//     case Action.STEAL:
//       return "Steal";
//     case Action.BLOCK:
//       return "Blocks";
//     case Action.CHALLENGE:
//       return "Challenges";
//   }
// };

// const preActionText = (action: Action): string => {
//   switch (action) {
//     case Action.INCOME:
//       return "takes";
//     case Action.FOREIGN_AID:
//       return "attempts to take";
//     case Action.TAX:
//       return "attempts to take";
//     case Action.EXCHANGE:
//       return "attempts to";
//     case Action.ASSASSINATE:
//       return "attempts to";
//     case Action.COUP:
//       return "organizes a";
//     case Action.STEAL:
//       return "attempts to";
//     default:
//       throw new Error("Should not get here");
//   }
// };

// function ActorPart({ player }: { player: Player }) {
//   return <span className={styles.actor}>{player.name}</span>;
// }

// function ActionPart({ event }: { event: GameEvent }) {
//   return <span className={styles.action}>{actionNameText(event.action)}</span>;
// }

// function PreActionPart({ event }: { event: GameEvent }) {
//   if (event.action === Action.BLOCK || event.action === Action.CHALLENGE) {
//     return null;
//   }
//   return (
//     <span className={styles.action}>
//       {event.coinsSpent != null
//         ? `spends ${event.coinsSpent} coins and `
//         : null}
//       {preActionText(event.action)}
//     </span>
//   );
// }

// function PostActionPart({ event }: { event: GameEvent }) {
//   if (!event.target) {
//     return null;
//   }

//   const preTarget = event.action === Action.STEAL ? " from " : " ";
//   return (
//     <span className={styles.postAction}>
//       {preTarget}
//       <ActorPart player={event.target} />
//     </span>
//   );
// }

function EventLine({ event }: { event: GameEvent }) {
  return (
    <span>
      {event.message}
      {/* <ActorPart player={event.actor} /> <PreActionPart event={event} />{" "}
      <ActionPart event={event} /> <PostActionPart event={event} />{" "} */}
    </span>
  );
}

// function ResponseLine({ event }: { event: GameEvent }) {
//   return (
//     <HGroup className={styles.response}>
//       {event.action === Action.BLOCK ? <FaShieldHalved /> : <FaCircleXmark />}
//       <GameLogEventInner event={event} />
//     </HGroup>
//   );
// }

// function RevealPart({ event }: { event: GameEvent }) {
//   if (event.targetRevealed == null || event.target == null) {
//     return null;
//   }

//   return (
//     <span className={styles.reveal}>
//       <ActorPart player={event.target} />
//       revealed
//       <Influence influence={event.targetRevealed} />
//     </span>
//   );
// }

// function OutcomeLine({ event }: { event: GameEvent }) {
//   if (event.response != null && event.response.outcome === Outcome.PENDING) {
//     return null;
//   }

//   if (event.outcome === Outcome.PENDING) {
//     return (
//       <div className={styles.response}>
//         <FaSpinner className={styles.spinner} />
//       </div>
//     );
//   }

//   return (
//     <div className={styles.response}>
//       {event.outcome === Outcome.SUCCESS ? "Success!" : "Failure!"} -{" "}
//       <RevealPart event={event} />
//     </div>
//   );
// }

function GameLogEventInner({ event }: { event: GameEvent }) {
  return (
    <div className={styles.inner}>
      <p className={styles.message}>
        <EventLine event={event} />
      </p>
      {/* {event.response ? <ResponseLine event={event.response} /> : null}
      <OutcomeLine event={event} /> */}
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
