function Help() {
  return (
    <section>
      <h3 className="font-bold">Turns</h3>
      <p>Each turn, a player takes one of the following actions</p>
      <ul className="ml-4 mt-2">
        <li>
          <p className="mb-2">
            <b>Income</b>
            <br />
            Take <b>1</b> coin from the treasury.
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b>Foreign Aid</b>
            <br />
            Take <b>2</b> coins from the treasury (Can be blocked by a{" "}
            <b className="text-influence-duke">Duke</b>).
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b>Coup</b>
            <br />
            Pay <b>7</b> coins to the treasury and choose another player to lose
            one influence. This cannot be blocked. If you have <b>10</b> or more
            coins, you must Coup.
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b>Character Action</b>
            <br />
            Perform one of the character actions (See below). You can perform
            any character action, even if you do not have this influence, though
            you can also be challenged by other players.
          </p>
        </li>
      </ul>
      <h3 className="font-bold mt-8">Character Actions</h3>
      <p>
        There are five different character cards in Coup, and each card has a
        unique action associated with it
      </p>
      <ul className="ml-4 mt-2">
        <li>
          <p className="mb-2">
            <b className="text-influence-duke">Duke</b>
            <br />
            Can perform the <b>Tax</b> action, taking <b>3</b> coins from the
            treasury.
            <br />
            Can also block <b>Foreign Aid</b>.
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b className="text-influence-assassin">Assassin</b>
            <br />
            Can perform the <b>Assassinate</b> action, paying <b>3</b> coins to
            target and eliminate another player's influence.
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b className="text-influence-captain">Captain</b>
            <br />
            Can perform the <b>Steal</b> action, taking <b>2</b> coins from
            another player.
            <br />
            Can also block <b>Steal</b> attempts against them.
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b className="text-influence-ambassador">Ambassador</b>
            <br />
            Can perform the <b>Exchange</b> action, which allows them to draw{" "}
            <b>2</b> cards from the top of the deck and return <b>2</b> cards to
            the dock (Optionally exchanging their own while doing so).
            <br />
            Can also block <b>Steal</b> attempts against them.
          </p>
        </li>
        <li>
          <p className="mb-2">
            <b className="text-influence-contessa">Contessa</b>
            <br />
            Can block <b>Assassinate</b> attempts against them.
          </p>
        </li>
      </ul>
      <h3 className="font-bold mt-8">Challenges</h3>
      <p>
        If a player announces a character action (other than <b>Income</b> or{" "}
        <b>Foreign Aid</b>), any other player can challenge them. The player
        whose action was challenged must then reveal the relevant influence. If
        they have the influence, they return it to the deck and draw a new one,
        and the challenger loses an influence. If they don't have it, they lose
        an influence.
      </p>
      <h3 className="font-bold mt-8">Winning the game</h3>
      <p>
        When a player loses both their influence cards, they are out of the
        game. Their cards are revealed to all players, and they no longer
        participate in the game. The last remaining player with influence wins
        the game.
      </p>
    </section>
  );
}

export default Help;

// The game proceeds in clockwise order, and on a player's turn, they can take one of the following actions:

// Income: Take 1 coin from the treasury.

// Foreign Aid: Announce that you're taking foreign aid (taking 2 coins from the treasury). Other players can challenge you, but if you do have a Duke, the challenger loses one influence. If you don't have a Duke, you lose an influence. (Challenges are a way to verify if someone is bluffing.)

// Coup: Pay 7 coins to the treasury and choose another player to lose one influence (reveal and discard one of their cards). The targeted player doesn't get a chance to block this action.

// Character Actions: Announce one of the character actions (Tax, Assassinate, Steal, or Exchange) even if you don't have the corresponding character. Other players can challenge you, and if you are bluffing, you lose one influence. If you do have the character, carry out the action as described earlier.

// Challenges:
// If a player announces a character action (other than Income or Foreign Aid), any other player can challenge them. To challenge, the accusing player states, "I challenge your claim." The player whose action was challenged must then reveal the relevant character card. If they have the card, the challenger loses an influence, but if they don't have the card, the player who made the false claim loses an influence.

// Losing Influence:
// When a player loses both their influence cards, they are out of the game. Their cards are revealed to all players, and they no longer participate in the game. The last remaining player with influence wins the game.
