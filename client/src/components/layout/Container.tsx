import { ReactNode } from "react";
import styles from "./Container.module.css";

type Props = {
  children: ReactNode;
};

function Container({ children }: Props) {
  return <div className={styles.container}>{children}</div>;
}

export default Container;
