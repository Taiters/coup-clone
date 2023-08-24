import { ReactNode } from "react";

type Props = {
  heading: string;
  subheading: string | ReactNode;
};

function PageTitle({ heading, subheading }: Props) {
  return (
    <hgroup className="mt-36 mb-10 text-center text-brown">
      <h1 className="text-5xl font-normal m-0">{heading}</h1>
      {subheading != null ? <p className="m-0">{subheading}</p> : null}
    </hgroup>
  );
}

export default PageTitle;
