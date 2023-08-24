import { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

function TopBar({ children }: Props) {
  return (
    <div className="py-2 text-xl border-b border-solid border-b-darkbrown">
      {children}
    </div>
  );
}

export default TopBar;
