import {FaUser, FaWifi} from "react-icons/fa6";
import Card from "./Card";
import Flex from "./Flex";
import styles from "./PlayerCard.module.css";

function PlayerCard() {
    return (
        <Card>
            <Flex>
            <FaUser color="#F0F" />
            <span>Danny boy</span>

            <div className={styles.right}>
                <Flex>
                    <FaWifi />
                </Flex>
            </div>
            </Flex>
        </Card>
    )
}

export default PlayerCard;