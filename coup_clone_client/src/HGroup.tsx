import { ReactNode } from "react";
import styles from "./HGroup.module.css";

type Props = {
    children: ReactNode,
}

function HGroup({children}: Props) {
    return (
        <div className={styles.hgroup}>
            {children}
        </div>
    )
}

export default HGroup;