import { ReactNode } from "react";
import styles from "./HGroup.module.css";

type Props = {
    children: ReactNode,
    className?: string | undefined,
    gap?: number | string | undefined,
}

function HGroup({children, className, gap}: Props) {
    const cls = className != null 
        ? `${styles.hgroup} ${className}`
        : styles.hgroup;
    
    const extraStyles = {
        gap,
    }

    return (
        <div style={extraStyles} className={cls}>
            {children}
        </div>
    )
}

export default HGroup;