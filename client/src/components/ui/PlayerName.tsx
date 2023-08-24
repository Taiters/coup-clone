import { FaUser } from "react-icons/fa6";
import HGroup from "../layout/HGroup";

type Props = {
  name: string;
  isCurrentTurn?: boolean;
};

function PlayerName({ name, isCurrentTurn = false }: Props) {
  return (
    <HGroup className="items-center">
      {isCurrentTurn ? ">" : null}
      <FaUser />
      {name}
    </HGroup>
  );
}

export default PlayerName;
