import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string | undefined;
};

function VGroup({ children, className }: Props) {
  return <div className={`flex flex-col gap-2 ${className}`}>{children}</div>;
}

export default VGroup;
