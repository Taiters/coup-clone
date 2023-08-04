import styles from "./Button.module.css";

export enum ButtonStyle {
    NORMAL,
    TAX,
    STEAL,
    ASSASSINATE,
    EXCHANGE,
}

type Props = {
    label: string,
    description: string,
    buttonStyle?: ButtonStyle,
}

const STYLE_MAP = {
    [ButtonStyle.NORMAL]: styles.normal,
    [ButtonStyle.TAX]: styles.tax,
    [ButtonStyle.STEAL]: styles.steal,
    [ButtonStyle.ASSASSINATE]: styles.assassinate,
    [ButtonStyle.EXCHANGE]: styles.exchange,
}

function Button({
    label,
    description,
    buttonStyle = ButtonStyle.NORMAL
}: Props) {
    const buttonClassNames = `${styles.button} ${STYLE_MAP[buttonStyle]}`;
    return (
        <button className={buttonClassNames}>
            {label}
            {description != null ? <span className={styles.description}>{description}</span> : null}
        </button>
    )
}

export default Button;