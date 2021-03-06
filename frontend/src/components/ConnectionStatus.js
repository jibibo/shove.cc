import { useState } from "react";

import { socket } from "../connection";

import "./ConnectionStatus.css";

let deaf = true;

function ConnectionStatus() {
    const [status, setStatus] = useState({
        text: "Ready to connect",
        color: "#999622",
    });
    const [visible, setVisible] = useState(true);

    function clicked(e) {
        setVisible(false);
    }

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            console.debug("> ConnectionStatus connect event");
            setStatus({
                text: "Connected!",
                color: "green",
            });
            setVisible(true);
        });

        socket.on("connect_error", () => {
            console.debug("> ConnectionStatus connect_error event");
            setStatus({
                text: "Error on connect, backend offline?",
                color: "#f8d7da",
            });
            setVisible(true);
        });

        socket.on("disconnect", (reason) => {
            console.debug("> ConnectionStatus disconnected event", reason);
            setStatus({
                text: "disconnected" + reason,
                color: "#f8d7da",
            });
            setVisible(true);
        });

        // socket.on("client_connected", (packet) => {
        //     console.debug("> ConnectionStatus client_connected", packet);
        //     if (packet["you"]) {
        //         setSid(packet["sid"]);
        //     }
        // });
    }

    return (
        <div
            style={{ backgroundColor: status.color }}
            className="status"
            onClick={clicked}
            hidden={!visible}
        >
            Connection status: {status.text}
        </div>
    );
}

export default ConnectionStatus;
