import { FaSpinner } from "react-icons/fa6";
import VGroup from "./layout/VGroup";

function Initializing() {
  return (
    <VGroup className="justify-center items-center h-full text-brown">
      <FaSpinner className="spinner" />
      <h1 className="text-2xl">Connecting</h1>
    </VGroup>
  );
}

export default Initializing;
