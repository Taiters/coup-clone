import styles from "./Button.module.css";

type Props = {
  label: string;
  disabled?: boolean;
  onClick?: () => void;
};
function Button({ label, onClick, disabled = false }: Props) {
  return (
    <button
      disabled={disabled}
      className={`${styles.button} ${disabled ? styles.disabled : null}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

export default Button;
