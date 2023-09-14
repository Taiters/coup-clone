import { useEventEmitter } from "../socket";
import { Game, Player, PlayerInfluence, TurnAction } from "../types";
import { nullthrows, titleCase } from "../utils";
import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";

type Props = {
  currentPlayer: Player;
  players: Player[];
  game: Game;
};

function AttemptedTurnMenu({ game, players, currentPlayer }: Props) {
  const [emitAcceptAction, isAcceptActionInFlight] =
    useEventEmitter("accept_action");
  const [emitChallenge, isChallengeInFlight] = useEventEmitter("challenge");
  const [emitBlock, isBlockInFlight] = useEventEmitter("block");

  if (currentPlayer.isCurrentTurn) {
    return (
      <p>
        You've attempted{" "}
        <span className="italic">{titleCase(TurnAction[game.turnAction])}</span>
        {game.turnTarget && ` against ${game.turnTarget.name}`}
      </p>
    );
  }

  if (currentPlayer.acceptsAction) {
    const waitingForPlayers = players.filter(
      (p) =>
        p.id !== nullthrows(game.currentTurn?.id) &&
        (p.influenceA === PlayerInfluence.UNKNOWN ||
          p.influenceB === PlayerInfluence.UNKNOWN),
    );
    const accepted = waitingForPlayers.filter((p) => p.acceptsAction);
    return (
      <p>
        Waiting for other players ({accepted.length}/{waitingForPlayers.length})
      </p>
    );
  }

  const canBlock =
    game.turnAction === TurnAction.FOREIGN_AID ||
    (game.turnTarget?.id === currentPlayer.id &&
      (game.turnAction === TurnAction.STEAL ||
        game.turnAction === TurnAction.ASSASSINATE));

  const canChallenge =
    game.turnAction !== TurnAction.FOREIGN_AID &&
    game.turnAction !== TurnAction.INCOME &&
    game.turnAction !== TurnAction.COUP;

  return (
    <VGroup>
      <p>
        {nullthrows(game.currentTurn?.name)} has attempted{" "}
        <span className="italic">{TurnAction[game.turnAction]}</span>
        {game.turnTarget && ` against ${game.turnTarget.name}`}
      </p>
      <HGroup>
        <Button
          className="w-full"
          label="Accept"
          onClick={() => emitAcceptAction()}
          pending={isAcceptActionInFlight}
        />
        {canChallenge && (
          <Button
            className="w-full"
            label="Challenge"
            onClick={() => emitChallenge()}
            pending={isChallengeInFlight}
          />
        )}
        {canBlock && (
          <Button
            className="w-full"
            label="Block"
            onClick={() => emitBlock()}
            pending={isBlockInFlight}
          />
        )}
      </HGroup>
    </VGroup>
  );
}

export default AttemptedTurnMenu;
