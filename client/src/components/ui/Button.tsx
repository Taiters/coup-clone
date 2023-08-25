export type ButtonProps = {
  label: string;
  small?: boolean;
} & React.ComponentPropsWithoutRef<"button">;

function Button({
  label,
  small = false,
  disabled = false,
  color = undefined,
  className = undefined,
  ...rest
}: ButtonProps) {
  const colorClass = disabled ? "bg-gray" : color ? color : "bg-purple";
  return (
    <button
      style={{
        fontSize: small ? "0.75em" : undefined,
      }}
      disabled={disabled}
      className={`${className} ${colorClass} ${
        disabled ? "cursor-auto" : "cursor-pointer"
      } rounded-none border-none px-8 text-white h-10`}
      {...rest}
    >
      {label}
    </button>
  );
}

export default Button;
