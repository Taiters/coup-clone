import { FaUser } from "react-icons/fa6";
import PlayerName from "./ui/PlayerName";
import HGroup from "./layout/HGroup";
import { Player, PlayerState } from "../types";

type Props = {
  player?: Player;
  current?: boolean;
};

function LobbyPlayer({ player, current = false }: Props) {
  if (player == null) {
    return (
      <div className="w-40 mx-auto">
        <HGroup className="text-darkgray items-center">
          <FaUser />
          Waiting for player...
        </HGroup>
      </div>
    );
  }

  return (
    <div className="w-40 mx-auto">
      {player.state === PlayerState.READY ? (
        <div className={current ? "text-purple" : ""}>
          <PlayerName name={player.name} />
        </div>
      ) : (
        <HGroup className="text-darkgray items-center">
          <FaUser />
          Joining...
        </HGroup>
      )}
    </div>
  );
}

export default LobbyPlayer;
