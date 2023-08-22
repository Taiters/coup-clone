import { Player } from "../types";

type Props = {
  playerToReveal: Player;
  currentPlayer: Player;
};

function RevealingActionMenu({ playerToReveal, currentPlayer }: Props) {
  if (playerToReveal.id === currentPlayer.id) {
    return <p>You must reveal an influence</p>;
  }

  return <p>Waiting for {playerToReveal.name} to reveal an influence</p>;
}

export default RevealingActionMenu;
