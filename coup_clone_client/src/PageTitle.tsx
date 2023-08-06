import { ReactNode } from "react";
import styles from "./PageTitle.module.css";

type Props = {
    heading: string,
    subheading: string | ReactNode,
}

function PageTitle({heading, subheading}: Props) {
    return (
        <hgroup className={styles.title}>
            <h1>{heading}</h1>
            {subheading != null ? <p>{subheading}</p> : null}
        </hgroup>
    )
}

export default PageTitle;