import { socket } from "./socket";

function LeaveButton() {
    const leaveGame = () => {
        socket.emit('leave_game');
    }
    return <a href="#" onClick={leaveGame}>Leave Game</a>;
}

export default LeaveButton;