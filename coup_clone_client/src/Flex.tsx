import { ReactNode, CSSProperties } from "react";
import styles from "./Flex.module.css";

type Props = {
    width?: number | string | undefined,
    grow?: number | undefined,
    alignItems?: string | undefined,
    direction?: "row" | "column",
    children: ReactNode,
}

function Flex({
    width,
    grow,
    alignItems,
    direction="row",
    children,
}: Props) {
    const s: CSSProperties = {
        flexDirection: direction,
        alignItems: alignItems != null 
            ? alignItems 
            :  direction === "row" ? "flex-start" : "stretch",
        flexGrow: grow,
        width,
    };

    return (
        <div className={styles.flex} style={s}>
            {children}
        </div>
    )
}

export default Flex;