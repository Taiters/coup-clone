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
  const emitEvent = useEventEmitter();

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
    emitEvent("take_action", { action: targetedAction, target: player.id });
    setTargetedAction(null);
  };

  return (
    <>
      <VGroup>
        <HGroup>
          <VGroup className="w-full">
            <Button
              label="Income"
              onClick={() =>
                emitEvent("take_action", { action: TurnAction.INCOME })
              }
            />
            <Button
              label="Tax"
              onClick={() =>
                emitEvent("take_action", { action: TurnAction.TAX })
              }
            />
            <Button
              label="Exchange"
              onClick={() =>
                emitEvent("take_action", { action: TurnAction.EXCHANGE })
              }
            />
          </VGroup>
          <VGroup className="w-full">
            <Button
              label="Foreign Aid"
              onClick={() =>
                emitEvent("take_action", { action: TurnAction.FOREIGN_AID })
              }
            />
            <Button
              disabled={currentPlayer.coins < 3}
              label="Assassinate"
              onClick={() => setTargetedAction(TurnAction.ASSASSINATE)}
            />
            <Button
              label="Steal"
              onClick={() => setTargetedAction(TurnAction.STEAL)}
            />
          </VGroup>
        </HGroup>
        <Button
          disabled={currentPlayer.coins < 7}
          label="Coup"
          onClick={() => setTargetedAction(TurnAction.COUP)}
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
