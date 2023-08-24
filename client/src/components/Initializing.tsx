import { FaSpinner } from "react-icons/fa6";

function Initializing() {
  return (
    <div className="flex flex-col justify-center items-center h-full text-brown">
      <FaSpinner className="spinner" />
      <h1>Connecting</h1>
    </div>
  );
}

export default Initializing;
