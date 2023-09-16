import { Player } from "../types";
import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import Button from "./ui/Button";
import Modal from "./ui/Modal";
import PlayerName from "./ui/PlayerName";

type Props = {
  players: Player[];
  onSelect: (player: Player) => void;
  onClose: () => void;
};

function PlayerSelector({ players, onSelect, onClose }: Props) {
  return (
    <Modal heading="Select target" onClose={onClose}>
      <VGroup>
        {players.map((p) => (
          <HGroup key={p.id} className="justify-between content-center">
            <PlayerName name={p.name} />
            <Button small label="Select" onClick={() => onSelect(p)} />
          </HGroup>
        ))}
      </VGroup>
    </Modal>
  );
}

export default PlayerSelector;
