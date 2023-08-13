import { ReactNode } from "react";
import styles from "./TopBar.module.css";

type Props = {
  children: ReactNode;
};

function TopBar({ children }: Props) {
  return <div className={styles.container}>{children}</div>;
}

export default TopBar;
