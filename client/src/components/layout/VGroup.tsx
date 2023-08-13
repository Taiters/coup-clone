import { ReactNode } from "react";
import styles from "./VGroup.module.css";

type Props = {
    children: ReactNode,
    className?: string | undefined,
}

function VGroup({children, className}: Props) {
    const cls = className != null 
        ? `${styles.vgroup} ${className}`
        : styles.vgroup;

    return (
        <div className={cls}>
            {children}
        </div>
    )
}

export default VGroup;