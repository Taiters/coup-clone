import HGroup from "./layout/HGroup";
import VGroup from "./layout/VGroup";
import styles from "./ActionMenu.module.css";
import Button from "./ui/Button";
import { socket } from "../socket";
import { Action } from "../types";

function ActionMenu() {
  return (
    <VGroup>
      <HGroup>
        <VGroup className={styles.buttonStack}>
          <Button
            label="Income"
            onClick={() =>
              socket.emit("take_action", { action: Action.INCOME })
            }
          />
          <Button
            label="Tax"
            onClick={() => socket.emit("take_action", { action: Action.TAX })}
          />
          <Button
            label="Exchange"
            onClick={() =>
              socket.emit("take_action", { action: Action.EXCHANGE })
            }
          />
        </VGroup>
        <VGroup className={styles.buttonStack}>
          <Button
            label="Foreign Aid"
            onClick={() =>
              socket.emit("take_action", { action: Action.FOREIGN_AID })
            }
          />
          <Button
            label="Assassinate"
            onClick={() =>
              socket.emit("take_action", { action: Action.ASSASSINATE })
            }
          />
          <Button
            label="Steal"
            onClick={() => socket.emit("take_action", { action: Action.STEAL })}
          />
        </VGroup>
      </HGroup>
      <Button
        label="Coup"
        onClick={() => socket.emit("take_action", { action: Action.COUP })}
      />
    </VGroup>
  );
}

export default ActionMenu;
