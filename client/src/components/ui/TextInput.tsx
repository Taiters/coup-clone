import { useState } from "react";

type Props = {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  validate?: ((value: string) => string | null) | null;
};

function TextInput({ value, placeholder, onChange, validate = null }: Props) {
  const [shouldValidate, setShouldValidate] = useState(false);
  const error = shouldValidate && validate != null ? validate(value) : null;

  return (
    <div className="w-full">
    <input
      value={value}
      onBlur={() => setShouldValidate(true)}
      onChange={(e) => {
        setShouldValidate(false);
        onChange(e.target.value);
      }}
      className="text-lightbrown bg-darkbrown rounded-none border-2 border-solid border-lightbrown px-4 h-10 w-full box-border"
      type="text"
      placeholder={placeholder}
    />
    <p className="text-red h-4">{error}</p>
    </div>
  );
}

export default TextInput;
