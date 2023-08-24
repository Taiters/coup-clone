import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";
import { socket } from "../socket";
import { Player, PlayerInfluence, TurnAction } from "../types";
import { useState } from "react";
import PlayerSelector from "./PlayerSelector";

type Props = {
  currentPlayer: Player;
  players: Player[];
};

function CurrentTurn({ currentPlayer, players }: Props) {
  const [targetedAction, setTargetedAction] = useState<TurnAction | null>(null);

  const onSelectTarget = (player: Player) => {
    if (targetedAction == null) {
      throw new Error("Did not expect this");
    }
    socket.emit("take_action", { action: targetedAction, target: player.id });
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
                socket.emit("take_action", { action: TurnAction.INCOME })
              }
            />
            <Button
              label="Tax"
              onClick={() =>
                socket.emit("take_action", { action: TurnAction.TAX })
              }
            />
            <Button
              label="Exchange"
              onClick={() =>
                socket.emit("take_action", { action: TurnAction.EXCHANGE })
              }
            />
          </VGroup>
          <VGroup className="w-full">
            <Button
              label="Foreign Aid"
              onClick={() =>
                socket.emit("take_action", { action: TurnAction.FOREIGN_AID })
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

export default CurrentTurn;
