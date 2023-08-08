import styles from "./Button.module.css";

type Props = {
    label: string,
    onClick?: () => void,
}
function Button({
    label,
    onClick,
}: Props) {
    return (
        <button className={styles.button} onClick={onClick}>
            {label}
        </button>
    )
}

export default Button;