import { FaCoins } from "react-icons/fa6";
import HGroup from "../layout/HGroup";

type Props = {
  value: number;
};

function Coins({ value }: Props) {
  return (
    <span className="text-right">
      <HGroup gap="0.25em">
        {value}
        <FaCoins />
      </HGroup>
    </span>
  );
}

export default Coins;
