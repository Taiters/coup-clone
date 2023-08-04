import Button, { ButtonStyle } from "./Button";
import Card from "./Card";

import styles from "./TurnActions.module.css";

function TurnActions() {
    return (
        <Card heading="Actions" subheading="What's your next move?">
            <menu className={styles.actions}>
                <li>
                    <Button label="Income" description="Take 1 coin" />
                </li>
                <li>
                    <Button label="Foreign Aid" description="Take 2 coins" />
                </li>
                <li>
                    <Button label="Tax" description="Take 3 coins" buttonStyle={ButtonStyle.TAX} />
                </li>
                <li>
                    <Button label="Steal" description="Take 2 coins from another player" buttonStyle={ButtonStyle.STEAL} />
                </li>
                <li>
                    <Button label="Assassinate" description="Pay 3 coins, choose player to lose influence" buttonStyle={ButtonStyle.ASSASSINATE} />
                </li>
                <li>
                    <Button label="Exchange" description="Take 2 cards, return 2 cards to court deck" buttonStyle={ButtonStyle.EXCHANGE} />
                </li>
                <li>
                    <Button label="Coup" description="Pay 7 coins, choose player to lose influence" />
                </li>
            </menu>
        </Card>
    );
}

export default TurnActions;