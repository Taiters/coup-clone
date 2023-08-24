import { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

function Container({ children }: Props) {
  return <div className="my-0 mx-auto max-w-screen-sm px-2">{children}</div>;
}

export default Container;
