import { useContext } from "react";

import Button from "@material-ui/core/Button";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import MeetingRoomIcon from "@material-ui/icons/MeetingRoom";

import { sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./HeaderRoomButtons.css";

function HeaderRoomButtons() {
    const { roomData, roomList } = useContext(GlobalContext);

    function onClickJoinRoom(room_name) {
        sendPacket("join_room", {
            room_name,
        });
    }

    function onClickLeaveRoom() {
        sendPacket("leave_room", {});
    }

    return (
        <div className="room-buttons-container">
            {roomData ? (
                <Button
                    variant="outlined"
                    color="secondary"
                    endIcon={<MeetingRoomIcon />}
                    onClick={onClickLeaveRoom}
                >
                    Leave {roomData.name}
                </Button>
            ) : (
                roomList.map((room, i) => {
                    return (
                        <div className="room-button" key={i}>
                            <Button
                                variant="contained"
                                startIcon={<PlayArrowIcon />}
                                onClick={() => {
                                    onClickJoinRoom(room.name);
                                }}
                            >
                                {room.name} ({room.user_count} /{" "}
                                {room.max_user_count})
                            </Button>
                        </div>
                    );
                })
            )}
        </div>
    );
}

export default HeaderRoomButtons;
