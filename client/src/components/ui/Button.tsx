import { FaSpinner } from "react-icons/fa6";

export type ButtonProps = {
  label: string;
  small?: boolean;
  pending?: boolean;
} & React.ComponentPropsWithoutRef<"button">;

function Button({
  label,
  small = false,
  pending = false,
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
      disabled={disabled || pending}
      className={`${className} ${colorClass} ${
        disabled || pending
          ? "cursor-auto"
          : "cursor-pointer hover:brightness-90"
      } rounded-none border-none px-8 text-white text-center h-10`}
      {...rest}
    >
      {pending ? <FaSpinner className="animate-spin inline" /> : label}
    </button>
  );
}

export default Button;
