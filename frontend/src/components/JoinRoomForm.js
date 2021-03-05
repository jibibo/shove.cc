import { useState } from "react";

import { sendPacket } from "../connection";

function JoinRoomForm() {
    // const [roomName, setRoomName] = useState(undefined);

    return (
        <div className="join-room-form">
            <form onSubmit={onJoinRoomFormSubmit}>
                <input
                    type="text form-control"
                    id="join-room-input"
                    placeholder="Enter room to join"
                />
            </form>
        </div>
    );
}

function onJoinRoomFormSubmit(e) {
    e.preventDefault();
    const roomName = document.getElementById("join-room-input").value;
    document.getElementById("join-room-input").value = "";
    sendPacket({
        model: "join_room",
        room_name: roomName,
    });
}

export default JoinRoomForm;
