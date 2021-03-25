import { useContext } from "react";

import Button from "@material-ui/core/Button";
import ArrowRightIcon from "@material-ui/icons/ArrowRight";

import { sendPacket } from "../connection";
import { GlobalContext } from "./GlobalContext";

import "./RoomList.css";

function RoomList() {
    const { roomList } = useContext(GlobalContext);

    function onClickJoinRoom(room_name) {
        sendPacket("join_room", {
            room_name,
        });
    }

    return (
        <div className="room-list">
            {roomList.map((room, i) => {
                return (
                    <div className="room-list-entry" key={i}>
                        <Button
                            variant="contained"
                            endIcon={<ArrowRightIcon />}
                            onClick={() => {
                                onClickJoinRoom(room.name);
                            }}
                        >
                            {room.name} ({room.user_count} /{" "}
                            {room.max_user_count})
                        </Button>
                    </div>
                );
            })}
        </div>
    );
}

export default RoomList;
