import styles from "./Button.module.css";

type Props = {
  label: string;
  disabled?: boolean;
  onClick?: () => void;
  small?: boolean;
};
function Button({ label, onClick, disabled = false, small = false }: Props) {
  return (
    <button
      style={{
        fontSize: small ? "0.75em" : undefined,
      }}
      disabled={disabled}
      className={`${styles.button} ${disabled ? styles.disabled : null}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

export default Button;
