import { useState, useContext } from "react";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

let deaf = true;

function RoomsList() {
    const [roomsList, setRoomsList] = useState([]);
    const { setRoom } = useContext(GlobalContext);

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            console.debug("> RoomsList connect event");
            sendPacket("get_rooms", {
                properties: ["name"],
            });
        });
        socket.on("room_list", (packet) => {
            console.debug("> RoomsList room_list", packet);
            setRoomsList(packet["rooms"]);
        });
        socket.on("join_room_status", (packet) => {
            console.debug("> RoomsList join_room_status", packet);
            setRoom(packet["room_name"]);
        });
    }

    return (
        <div className="rooms-list">
            Rooms:
            <br />
            {roomsList.map((room, i) => {
                return (
                    <div className="room-list-entry" key={i}>
                        <p key={i}>{room.name}</p>
                        <button
                            onClick={() => {
                                sendPacket("join_room", {
                                    room_name: room.name,
                                });
                            }}
                        >
                            Join room {room.name}!
                        </button>
                    </div>
                );
            })}
        </div>
    );
}

export default RoomsList;
