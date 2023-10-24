import { useState } from "react";
import { Game, Player, PlayerInfluence, TurnAction } from "../types";
import { useEventEmitter } from "../socket";
import VGroup from "./layout/VGroup";
import HGroup from "./layout/HGroup";
import Button from "./ui/Button";
import PlayerSelector from "./PlayerSelector";
import { nullthrows } from "../utils";

type Props = {
  game: Game;
  players: Player[];
  currentPlayer: Player;
};

function StartTurnMenu({ game, players, currentPlayer }: Props) {
  const [targetedAction, setTargetedAction] = useState<TurnAction | null>(null);
  const [emitTakeAction, isTakeActionInFlight] = useEventEmitter("take_action");

  if (!currentPlayer.isCurrentTurn) {
    return (
      <p className="m-0 py-2">
        Waiting for {nullthrows(game.currentTurn?.name)}
      </p>
    );
  }

  const onSelectTarget = (player: Player) => {
    if (targetedAction == null) {
      throw new Error("Did not expect this");
    }
    emitTakeAction({ action: targetedAction, target: player.id });
    setTargetedAction(null);
  };

  const mustCoup = currentPlayer.coins >= 10;

  return (
    <>
      <VGroup>
        <HGroup>
          <VGroup className="w-full">
            <Button
              label="Income"
              disabled={mustCoup}
              onClick={() => emitTakeAction({ action: TurnAction.INCOME })}
              pending={isTakeActionInFlight}
            />
            <Button
              label="Tax"
              disabled={mustCoup}
              onClick={() => emitTakeAction({ action: TurnAction.TAX })}
              pending={isTakeActionInFlight}
            />
            <Button
              label="Exchange"
              disabled={mustCoup}
              onClick={() => emitTakeAction({ action: TurnAction.EXCHANGE })}
              pending={isTakeActionInFlight}
            />
          </VGroup>
          <VGroup className="w-full">
            <Button
              label="Foreign Aid"
              disabled={mustCoup}
              onClick={() => emitTakeAction({ action: TurnAction.FOREIGN_AID })}
              pending={isTakeActionInFlight}
            />
            <Button
              disabled={currentPlayer.coins < 3 || mustCoup}
              label="Assassinate"
              onClick={() => setTargetedAction(TurnAction.ASSASSINATE)}
              pending={isTakeActionInFlight}
            />
            <Button
              label="Steal"
              disabled={mustCoup}
              onClick={() => setTargetedAction(TurnAction.STEAL)}
              pending={isTakeActionInFlight}
            />
          </VGroup>
        </HGroup>
        <Button
          disabled={currentPlayer.coins < 7}
          label="Coup"
          onClick={() => setTargetedAction(TurnAction.COUP)}
          pending={isTakeActionInFlight}
        />
      </VGroup>
      {targetedAction != null && (
        <PlayerSelector
          players={players.filter(
            (p) =>
              p.id !== currentPlayer.id &&
              (p.influenceA === PlayerInfluence.UNKNOWN ||
                p.influenceB === PlayerInfluence.UNKNOWN),
          )}
          onSelect={onSelectTarget}
          onClose={() => setTargetedAction(null)}
        />
      )}
    </>
  );
}

export default StartTurnMenu;
