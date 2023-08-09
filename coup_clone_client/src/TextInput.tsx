import styles from "./TextInput.module.css";

type Props = {
    placeholder: string,
    value: string,
    onChange: (value: string) => void,
}

function TextInput({value, placeholder, onChange}: Props) {
    return (
        <input 
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className={styles.input}
            type="text"
            placeholder={placeholder} />
    );
}

export default TextInput;