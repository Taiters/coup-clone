import { Player } from "../types";

type Props = {
  player: Player;
};

function WaitingForPlayer({ player }: Props) {
  return <p className="m-0 py-4">Waiting for {player.name}</p>;
}

export default WaitingForPlayer;
