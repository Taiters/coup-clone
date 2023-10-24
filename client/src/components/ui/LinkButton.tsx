import { FaSpinner } from "react-icons/fa6";

type Props = {
  label: string;
  pending?: boolean;
} & React.ComponentPropsWithoutRef<"button">;

function LinkButton({
  label,
  pending = false,
  className = undefined,
  ...rest
}: Props) {
  return (
    <button
      className={`inline text-left ${
        !pending ? "cursor-pointer hover:brightness-90" : ""
      } text-purple underline ${className}`}
      {...rest}
    >
      {pending ? <FaSpinner className="animate-spin" /> : label}
    </button>
  );
}

export default LinkButton;
