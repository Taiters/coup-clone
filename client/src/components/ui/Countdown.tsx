import { useEffect, useRef, useState } from "react";
import styles from "./Countdown.module.css";
import { request } from "http";

type Props = {
  from: Date;
  to: Date;
};

function Countdown({from, to }: Props) {
const [progress, setProgress] = useState(0);
const [now, setNow] = useState('');
const animationRef = useRef(0);

    const update = () => {
        const fromSeconds = from.getTime();
        const toSeconds = to.getTime();
        const nowSeconds = (new Date()).getTime();
        setProgress(Math.min(Math.max((nowSeconds-fromSeconds) / (toSeconds - fromSeconds), 0), 1));
        setNow((new Date()).toTimeString())
        animationRef.current = requestAnimationFrame(update);
    }

    useEffect(() => {
        animationRef.current = requestAnimationFrame(update);
        return () => cancelAnimationFrame(animationRef.current);
    }, []);

  return (
    <div className={styles.container}>
      <div
        className={styles.inner}
        style={{
          width: `${progress * 100}%`,
        }}
      />
      <h1>{progress}</h1>
      <h1>{from.toTimeString()}</h1>
      <h1>{to.toTimeString()}</h1>
      <h1>{(new Date()).toTimeString()}</h1>
      <h1>{now}</h1>
    </div>
  );
}

export default Countdown;
