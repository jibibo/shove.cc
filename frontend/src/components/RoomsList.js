import { useState, useContext } from "react";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./RoomsList.css";

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
                        <div className="room-info">
                            <div className="room-name">
                                <p>Room name: </p>
                                <p style={{ textIndent: 5 }}>{room.name}</p>
                            </div>
                            <div className="room-players">
                                <p>Players: <code>{room.players}/{room.max_players}</code></p>
                            </div>
                        </div>
                        <button
                            onClick={() => {
                                sendPacket("join_room", {
                                    room_name: room.name,
                                });
                            }}
                        >
                            Join room!
                        </button>
                    </div>
                );
            })}
        </div>
    );
}

export default RoomsList;
