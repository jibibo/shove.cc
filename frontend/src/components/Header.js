import { useContext } from "react";

import { GlobalContext } from "./GlobalContext";

import { sendPacket, socket } from "../connection";

import "./Header.css";

let deaf = true;

function Header() {
    const { money, setMoney, room, user } = useContext(GlobalContext);

    if (deaf) {
        deaf = false;

        socket.on("log_in_status", (packet) => {
            console.debug("> Header log_in_status", packet);
            if (packet["success"]) {
                sendPacket("get_account_data", {
                    username: packet["username"],
                });
            }
        });

        socket.on("get_account_data_status", (packet) => {
            console.debug("> Header get_account_data_status", packet);
            if (packet["success"]) {
                if (
                    user === undefined ||
                    packet["account"]["username"] === user
                ) {
                    setMoney(packet["account"]["money"]);
                }
            }
        });
    }

    return (
        <header>
            <div>
                <h4>
                    Logged in as: <b>{user}</b>
                </h4>
                <h4>
                    Money: <b>{money}</b>
                </h4>
                <h4>
                    Currently in room: <b>{room}</b>
                </h4>
            </div>
            <div className="header-button-container">
                <button className="header-button">
                    {user ? "Log out" : "Log in"}
                </button>
            </div>
        </header>
    );
}

export default Header;
