import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string | undefined;
  gap?: number | string | undefined;
};

function HGroup({ children, className, gap }: Props) {
  const extraStyles = {
    gap,
  };

  return (
    <div style={extraStyles} className={`flex gap-2 ${className}`}>
      {children}
    </div>
  );
}

export default HGroup;
