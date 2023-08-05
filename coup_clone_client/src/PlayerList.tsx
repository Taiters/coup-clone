import Flex from "./Flex";

import PlayerInfo, { PlayerInfluenceType } from "./PlayerInfo";

function PlayerList() {
    return (
        <Flex direction="column">
            <PlayerInfo name="Danny boy" coins={3} color="red" influence={[PlayerInfluenceType.UNKNOWN, PlayerInfluenceType.DUKE]} isConnected={true}/>
            <PlayerInfo name="Hank Schrader" coins={7} color="aqua" influence={[PlayerInfluenceType.UNKNOWN, PlayerInfluenceType.UNKNOWN]} isConnected={true}/>
            <PlayerInfo name="Steve Gomez" coins={14} color="purple" influence={[PlayerInfluenceType.CAPTAIN, PlayerInfluenceType.CONTESSA]} isConnected={false}/>
            <PlayerInfo name="Walter White" coins={1} color="green" influence={[PlayerInfluenceType.AMBASSADOR, PlayerInfluenceType.ASSASSIN]} isConnected={true}/>
        </Flex>
    );

}

export default PlayerList;