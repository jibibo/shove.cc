import { useState, useContext } from "react";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./RoomList.css";

let deaf = true;

function RoomList() {
    const [roomList, setRoomList] = useState([]);
    const { setRoom, user } = useContext(GlobalContext);

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            console.debug("> RoomList connect event");
            sendPacket("get_room_list", {
                properties: ["name"],
            });
        });
        socket.on("room_list", (packet) => {
            console.debug("> RoomList room_list", packet);
            setRoomList(packet["room_list"]);
        });
        socket.on("join_room_status", (packet) => {
            console.debug("> RoomList join_room_status", packet);
            if (packet["success"]) {
                setRoom(packet["room_name"]);
            }
        });
    }

    return (
        <div className="room-list">
            Rooms:
            <br />
            {roomList.map((room, i) => {
                return (
                    <div className="room-list-entry" key={i}>
                        <div className="room-info">
                            <p>
                                {room.name} - Users: {room.user_count} /{" "}
                                {room.max_user_count}
                            </p>
                        </div>
                        <button
                            onClick={() => {
                                sendPacket("join_room", {
                                    username: user,
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

export default RoomList;
