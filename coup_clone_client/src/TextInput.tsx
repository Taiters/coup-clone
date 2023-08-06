import styles from "./TextInput.module.css";

type Props = {
    placeholder: string,
}

function TextInput({placeholder}: Props) {
    return (
        <input 
            className={styles.input}
            type="text"
            placeholder={placeholder} />
    );
}

export default TextInput;