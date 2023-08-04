import Flex from "./Flex";

import PlayerInfo, { PlayerInfluenceType } from "./PlayerInfo";

function PlayerList() {
    return (
        <Flex direction="column">
            <PlayerInfo name="Danny boy" influence={[PlayerInfluenceType.UNKNOWN, PlayerInfluenceType.DUKE]} isConnected={true}/>
            <PlayerInfo name="Hank Schrader" influence={[PlayerInfluenceType.UNKNOWN, PlayerInfluenceType.UNKNOWN]} isConnected={true}/>
            <PlayerInfo name="Steve Gomez" influence={[PlayerInfluenceType.CAPTAIN, PlayerInfluenceType.CONTESSA]} isConnected={false}/>
            <PlayerInfo name="Walter White" influence={[PlayerInfluenceType.AMBASSADOR, PlayerInfluenceType.ASSASSIN]} isConnected={true}/>
        </Flex>
    );

}

export default PlayerList;