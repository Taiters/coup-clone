import { FaSquareXmark } from "react-icons/fa6";
import styles from "./Modal.module.css";
import { ReactNode } from "react";
import Container from "../layout/Container";

type Props = {
  heading: string;
  children: ReactNode;
  onClose?: () => void | null;
};

function Modal({ heading, children, onClose }: Props) {
  return (
    <div className={styles.container}>
      <Container>
        <div className={styles.modal}>
          <div className={styles.header}>
            <h3>{heading}</h3>
            {onClose && (
              <FaSquareXmark className={styles.close} onClick={onClose} />
            )}
          </div>
          <div className={styles.content}>{children}</div>
        </div>
      </Container>
    </div>
  );
}

export default Modal;
