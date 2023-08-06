import { ReactNode } from "react";
import styles from "./VGroup.module.css";

type Props = {
    children: ReactNode,
}

function VGroup({children}: Props) {
    return (
        <div className={styles.vgroup}>
            {children}
        </div>
    )
}

export default VGroup;