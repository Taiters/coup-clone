import { PlayerInfluence } from "../../types";

const INFLUENCE_NAMES = {
  [PlayerInfluence.UNKNOWN]: "???",
  [PlayerInfluence.AMBASSADOR]: "AMBASSADOR",
  [PlayerInfluence.ASSASSIN]: "ASSASSIN",
  [PlayerInfluence.CAPTAIN]: "CAPTAIN",
  [PlayerInfluence.DUKE]: "DUKE",
  [PlayerInfluence.CONTESSA]: "CONTESSA",
};

type Props = {
  influence: PlayerInfluence;
  revealed?: boolean;
};

function Influence({ influence, revealed = false }: Props) {
  return (
    <div
      className={`text-center font-bold relative text-influence-${PlayerInfluence[
        influence
      ].toLowerCase()} ${revealed && "opacity-50 grayscale-[50%]"}`}
    >
      {INFLUENCE_NAMES[influence]}
    </div>
  );
}

export default Influence;
