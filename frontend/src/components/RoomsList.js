import { useState, useEffect } from "react";

import { socket, sendPacket } from "../connection";

function RoomsList() {
    const [roomsList, setRoomsList] = useState([]);

    useEffect(() => {
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

        return () => {
            socket.off("room_list");
        };
    });

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
