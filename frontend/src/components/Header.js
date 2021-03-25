import { useContext } from "react";

import Button from "@material-ui/core/Button";
import MeetingRoomIcon from "@material-ui/icons/MeetingRoom";
import ExitToApp from "@material-ui/icons/ExitToApp";

import { GlobalContext } from "./GlobalContext";
import RoomList from "./RoomList";

import { sendPacket } from "../connection";
import { abbreviate } from "../formatting";

import "./Header.css";

function Header() {
    const { accountData, roomData } = useContext(GlobalContext);

    function onClickLeaveRoom(e) {
        sendPacket("leave_room", {});
    }

    function onClickLogOut(e) {
        sendPacket("log_out", {});
    }

    return (
        <header>
            <div>
                <div className="room-buttons">
                    {roomData ? (
                        <div className="leave-room-button-container">
                            <Button
                                variant="outlined"
                                color="secondary"
                                endIcon={<MeetingRoomIcon />}
                                onClick={onClickLeaveRoom}
                            >
                                Leave {roomData.name}
                            </Button>
                        </div>
                    ) : (
                        <RoomList />
                    )}
                </div>
            </div>
            <div>
                {accountData ? (
                    <>
                        <div className="log-out-button-container">
                            <span className="username-text">
                                User: <b>{accountData.username}</b>
                                {" / "}
                                <b>{abbreviate(accountData.money)}</b>
                            </span>
                            <Button
                                variant="outlined"
                                color="secondary"
                                endIcon={<ExitToApp />}
                                onClick={onClickLogOut}
                            >
                                Log out
                            </Button>
                        </div>
                    </>
                ) : null}
            </div>
        </header>
    );
}

export default Header;
