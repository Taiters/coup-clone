import { ReactNode } from "react"
import styles from "./Card.module.css";

type Props = {
    heading?: string,
    subheading?: string,
    children: ReactNode,
}

function Card({heading, subheading, children}: Props) {
    return (
        <section className={styles.card}>
            {heading != null ? (
                <hgroup className={styles.heading}>
                    <h1>{heading}</h1>
                    {subheading != null ? <p>{subheading}</p> : null}
                </hgroup>
            ) : null}
            {children}
        </section>
    )
}

export default Card;