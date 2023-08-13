import { FaCoins } from "react-icons/fa6";
import HGroup from "../layout/HGroup";
import styles from "./Coins.module.css";

type Props = {
  value: number;
};

function Coins({ value }: Props) {
  return (
    <span className={styles.coins}>
      <HGroup gap="0.25em">
        {value}
        <FaCoins />
      </HGroup>
    </span>
  );
}

export default Coins;
