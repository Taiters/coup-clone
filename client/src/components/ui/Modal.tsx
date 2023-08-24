import { FaSquareXmark } from "react-icons/fa6";
import { ReactNode } from "react";
import Container from "../layout/Container";

type Props = {
  heading: string;
  children: ReactNode;
  onClose?: () => void | null;
};

function Modal({ heading, children, onClose }: Props) {
  return (
    <div className="absolute inset-0 flex items-center bg-overlay">
      <Container>
        <div className="relative bg-yellow shadow-sm border border-solid border-brown mx-4">
          <div className="bg-lightbrown border-b border-b-brown overflow-auto flex justify-between items-center text-darkbrown">
            <h3 className="m-2">{heading}</h3>
            {onClose && (
              <FaSquareXmark
                className="block m-2 text-2xl cursor-pointer"
                onClick={onClose}
              />
            )}
          </div>
          <div className="m-2">{children}</div>
        </div>
      </Container>
    </div>
  );
}

export default Modal;
