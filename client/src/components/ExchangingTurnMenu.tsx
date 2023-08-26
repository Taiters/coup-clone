import { Game, Player, PlayerInfluence } from "../types";
import VGroup from "./layout/VGroup";
import InfluenceButton from "./ui/InfluenceButton";
import { nullthrows } from "../utils";
import { useEffect, useState } from "react";
import Button from "./ui/Button";
import HGroup from "./layout/HGroup";
import { socket } from "../socket";

type Props = {
  game: Game;
  currentPlayer: Player;
};

type ExchangingInfluence = {
  influence: PlayerInfluence;
  selected: boolean;
  enabled: boolean;
};

function Inner({ game, currentPlayer }: Props) {
  debugger;
  const hand = nullthrows(currentPlayer.hand);
  const [exchangingInfluence, setExchangingInfluence] = useState<
    ExchangingInfluence[]
  >([]);

  useEffect(() => {
    setExchangingInfluence([
      {
        influence: hand.influenceA,
        selected: false,
        enabled: currentPlayer.influenceA === PlayerInfluence.UNKNOWN,
      },
      {
        influence: hand.influenceB,
        selected: false,
        enabled: currentPlayer.influenceB === PlayerInfluence.UNKNOWN,
      },
      ...game.topOfDeck.map((i) => ({
        influence: i,
        selected: false,
        enabled: true,
      })),
    ]);
  }, [
    hand.influenceA,
    hand.influenceB,
    game.topOfDeck,
    currentPlayer.influenceA,
    currentPlayer.influenceB,
  ]);

  const selectedCount = exchangingInfluence.filter((i) => i.selected).length;
  const selectionLimit =
    2 -
    [
      currentPlayer.influenceA !== PlayerInfluence.UNKNOWN,
      currentPlayer.influenceB !== PlayerInfluence.UNKNOWN,
    ].filter((unknown) => unknown).length;
  const onToggleInfluence = (index: number) =>
    setExchangingInfluence((current) => {
      const copied = [...current];
      const toggling = copied[index];

      if (selectedCount === selectionLimit && !toggling.selected) {
        return copied;
      }

      copied[index] = {
        ...toggling,
        selected: !toggling.selected,
      };
      return copied;
    });

  const onExchange = () => {
    socket.emit(
      "exchange",
      exchangingInfluence.filter((e) => e.enabled),
    );
  };

  return (
    <VGroup>
      <p>
        Select {selectionLimit} card{selectionLimit > 1 && "s"} to keep
      </p>
      <HGroup>
        <VGroup className="w-full">
          {exchangingInfluence.slice(0, 2).map((exchange, i) => (
            <InfluenceButton
              key={i}
              onClick={() => onToggleInfluence(i)}
              disabled={
                !exchange.enabled ||
                (!exchange.selected && selectedCount === selectionLimit)
              }
              className={`${!exchange.selected ? "grayscale-[50%]" : ""}`}
              influence={exchange.influence}
            />
          ))}
        </VGroup>
        <VGroup className="w-full">
          {exchangingInfluence.slice(2).map((exchange, i) => (
            <InfluenceButton
              key={i + 2}
              disabled={
                !exchange.enabled ||
                (!exchange.selected && selectedCount === selectionLimit)
              }
              onClick={() => onToggleInfluence(i + 2)}
              className={`${!exchange.selected ? "grayscale-[50%]" : ""}`}
              influence={exchange.influence}
            />
          ))}
        </VGroup>
      </HGroup>
      <Button
        label={`Exchange (${selectedCount}/${selectionLimit})`}
        disabled={selectedCount !== selectionLimit}
        onClick={onExchange}
      />
    </VGroup>
  );
}

function ExchangingTurnMenu({ game, currentPlayer }: Props) {
  debugger;
  if (currentPlayer.id !== nullthrows(game.currentTurn?.id)) {
    return <p>Waiting for {nullthrows(game.currentTurn?.name)} to exchange</p>;
  }

  return <Inner game={game} currentPlayer={currentPlayer} />;
}

export default ExchangingTurnMenu;
