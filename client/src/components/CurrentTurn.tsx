import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import styles from "./CurrentTurn.module.css";
import Button from "./ui/Button";
import { socket } from "../socket";
import { TurnAction } from "../types";

function CurrentTurn() {
  return (
    <VGroup>
      <HGroup>
        <VGroup className={styles.buttonStack}>
          <Button
            label="Income"
            onClick={() =>
              socket.emit("take_action", { action: TurnAction.INCOME })
            }
          />
          <Button
            label="Tax"
            onClick={() => socket.emit("take_action", { action: TurnAction.TAX })}
          />
          <Button
            label="Exchange"
            onClick={() =>
              socket.emit("take_action", { action: TurnAction.EXCHANGE })
            }
          />
        </VGroup>
        <VGroup className={styles.buttonStack}>
          <Button
            label="Foreign Aid"
            onClick={() =>
              socket.emit("take_action", { action: TurnAction.FOREIGN_AID })
            }
          />
          <Button
            label="Assassinate"
            onClick={() =>
              socket.emit("take_action", { action: TurnAction.ASSASSINATE })
            }
          />
          <Button
            label="Steal"
            onClick={() => socket.emit("take_action", { action: TurnAction.STEAL })}
          />
        </VGroup>
      </HGroup>
      <Button
        label="Coup"
        onClick={() => socket.emit("take_action", { action: TurnAction.COUP })}
      />
    </VGroup>
  );
}

export default CurrentTurn;
