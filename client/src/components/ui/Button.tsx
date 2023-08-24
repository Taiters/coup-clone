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
      className={`rounded-none border-none px-8 cursor-pointer text-white h-10 ${
        disabled ? "bg-gray" : "bg-purple"
      } ${disabled ? "cursor-auto" : "cursor-pointer"}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

export default Button;
