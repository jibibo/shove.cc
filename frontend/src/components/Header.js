import { useContext } from "react";

import { GlobalContext } from "./GlobalContext";

import RoomList from "./RoomList";

import { socket } from "../connection";

import "./Header.css";

let deaf = true;

function Header() {
    const { accountData, setAccountData, roomName } = useContext(GlobalContext);

    if (deaf) {
        deaf = false;

        socket.on("log_in", (packet) => {
            console.debug("> Header log_in", packet, accountData);
            setAccountData(packet.account_data);
        });

        socket.on("account_data", (packet) => {
            console.debug("> Header account_data", packet, accountData);
            if (packet.account_data.username === accountData.username) {
                // "if undefined" is really bad, fix this
                setAccountData(packet.account_data);
            }
        });
    }

    return (
        <header>
            <div>
                <h4>
                    Logged in as: <b>{accountData.username}</b>
                </h4>
                <h4>
                    Money: <b>{accountData.money}</b>
                </h4>
                <h4>
                    Currently in room: <b>{roomName}</b>
                </h4>
            </div>
            <div className="room-list-container">
                <RoomList />
            </div>
        </header>
    );
}

export default Header;
