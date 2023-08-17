import { useEffect, useState } from "react";

type Props = {
    to: Date,
}

function Countdown({to}: Props) {
    const now = new Date();
    const seconds = (to.getTime() - now.getTime()) / 1000;
    const [secondsRemaining, setSecondsRemaining] = useState(0);

    useEffect(() => {
        const timer = window.setInterval(() => {
            const now = new Date();
            const seconds = (to.getTime() - now.getTime()) / 1000;
            setSecondsRemaining(Math.round(seconds));
        }, 500);
        return () => {
            window.clearInterval(timer);
        }
    }, [secondsRemaining, setSecondsRemaining]);

    return <span>{secondsRemaining}</span>;
}

export default Countdown;