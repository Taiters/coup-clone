import { FaSpinner } from "react-icons/fa6";

import styles from "./Initializing.module.css";

function Initializing() {
  return (
    <div className={styles.container}>
      <FaSpinner className="spinner" />
      <h1>Connecting</h1>
    </div>
  );
}

export default Initializing;
