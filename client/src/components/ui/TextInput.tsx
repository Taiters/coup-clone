type Props = {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
};

function TextInput({ value, placeholder, onChange }: Props) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="text-lightbrown bg-darkbrown rounded-none border-2 border-solid border-lightbrown px-4 h-10 w-full box-border"
      type="text"
      placeholder={placeholder}
    />
  );
}

export default TextInput;
