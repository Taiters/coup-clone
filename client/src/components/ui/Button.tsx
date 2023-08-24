type Props = {
  label: string;
  disabled?: boolean;
  onClick?: () => void;
  small?: boolean;
  className?: string | undefined;
  color?: string | null;
};
function Button({ label, onClick, disabled = false, small = false, className=undefined, color=null }: Props) {
  const colorClass = disabled ? "bg-gray" : color ? color : "bg-purple";
  return (
    <button
      style={{
        fontSize: small ? "0.75em" : undefined,
      }}
      disabled={disabled}
      className={`${className} ${colorClass} ${disabled ? "cursor-auto" : "cursor-pointer"} rounded-none border-none px-8 cursor-pointer text-white h-10`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

export default Button;
