import { PlayerInfluence } from "../../types";

const INFLUENCE_COLORS = {
  [PlayerInfluence.UNKNOWN]: "#8E8D7E",
  [PlayerInfluence.AMBASSADOR]: "#ADB55A",
  [PlayerInfluence.ASSASSIN]: "#689393",
  [PlayerInfluence.CAPTAIN]: "#4494DE",
  [PlayerInfluence.DUKE]: "#BF7BDF",
  [PlayerInfluence.CONTESSA]: "#DA7777",
};

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
      className={`text-center font-bold relative ${
        revealed && "opacity-50 grayscale-[50%]"
      }`}
      style={{
        color: INFLUENCE_COLORS[influence],
      }}
    >
      {INFLUENCE_NAMES[influence]}
    </div>
  );
}

export default Influence;
