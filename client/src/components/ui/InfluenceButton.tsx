import { PlayerInfluence } from "../../types";
import Button, { ButtonProps } from "./Button";

type Props = {
  influence: PlayerInfluence;
} & Omit<ButtonProps, "label">;

function InfluenceButton({ influence, ...rest }: Props) {
  return (
    <Button
      color={`bg-influence-${PlayerInfluence[influence].toLowerCase()}`}
      label={PlayerInfluence[influence]}
      {...rest}
    />
  );
}

export default InfluenceButton;
