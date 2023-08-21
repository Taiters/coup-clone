import { FaSquareXmark } from "react-icons/fa6";
import styles from "./Modal.module.css";

type Props = {
  heading: string;
  onClose?: () => void | null;
};

function Modal({ heading, onClose }: Props) {
  return (
    <div className={styles.container}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h3>{heading}</h3>
          {onClose && (
            <FaSquareXmark className={styles.close} onClick={onClose} />
          )}
        </div>
        <div className={styles.content}>
          <p>Some modal content</p>
        </div>
      </div>
    </div>
  );
}

export default Modal;
