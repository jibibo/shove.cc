import { useState } from "react";

import { socket } from "../connection";

import "./ConnectionStatus.css";

let deaf = true;

function ConnectionStatus() {
    const [status, setStatus] = useState({
        text: "ready to connect",
        color: "#999622",
    });
    const [visible, setVisible] = useState(true);

    function popup(text, color) {
        setStatus({
            text,
            color
        })
        setVisible(true);
        setTimeout(() => { // this should be cancelled when popup() gets called again, as it will vanish too quickly
            setVisible(false)
        }, 2000)
    }

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            console.debug("> ConnectionStatus connect event");
            popup("connected", "green");
        });

        socket.on("connect_error", () => {
            console.debug("> ConnectionStatus connect_error event");
            popup("error on connect, backend offline?", "darkred");
        });

        socket.on("disconnect", (reason) => {
            console.debug("> ConnectionStatus disconnect event:", reason);
            popup("disconnected", "darkred");
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
            hidden={!visible}
        >
            Connection status: {status.text}
        </div>
    );
}

export default ConnectionStatus;
