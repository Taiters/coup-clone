import styles from "./Button.module.css";

type Props = {
    label: string,
}
function Button({
    label,
}: Props) {
    return (
        <button className={styles.button}>
            {label}
        </button>
    )
}

export default Button;