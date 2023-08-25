type Props = {
  label: string;
} & React.ComponentPropsWithoutRef<"button">;

function LinkButton({ label, className = undefined, ...rest }: Props) {
  return (
    <button
      className={`inline text-left cursor-pointer text-purple underline ${className}`}
      {...rest}
    >
      {label}
    </button>
  );
}

export default LinkButton;
