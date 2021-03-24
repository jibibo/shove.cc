import { useState, useContext } from "react";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./RoomList.css";

let deaf = true;

function RoomList() {
    const [roomList, setRoomList] = useState([]);
    const { setRoomName } = useContext(GlobalContext);

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            console.debug("> RoomList connect event");
            sendPacket("get_room_list", {});
        });

        socket.on("room_list", (packet) => {
            console.debug("> RoomList room_list", packet);
            setRoomList(packet.room_list);
        });

        socket.on("join_room", (packet) => {
            console.debug("> RoomList join_room", packet);
            setRoomName(packet.room_name);
        });
    }

    return (
        <div className="room-list">
            {roomList.map((room, i) => {
                return (
                    <div className="room-list-entry" key={i}>
                        <button
                            onClick={() => {
                                sendPacket("join_room", {
                                    room_name: room.name,
                                });
                            }}
                        >
                            {room.name} ({room.user_count} /{" "}
                            {room.max_user_count})
                        </button>
                    </div>
                );
            })}
        </div>
    );
}

export default RoomList;
