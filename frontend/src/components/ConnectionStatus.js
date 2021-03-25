import { useState } from "react";

import { socket } from "../connection";

import "./ConnectionStatus.css";

let deaf = true;

function ConnectionStatus() {
    const [status, setStatus] = useState();
    const [visible, setVisible] = useState(false);

    function popup(text, color) {
        setStatus({
            text,
            color,
        });
        setVisible(true);
        setTimeout(() => {
            // this should be cancelled when popup() gets called again, as it will vanish too quickly
            setVisible(false);
        }, 2000);
    }

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            popup("connected", "green");
        });

        socket.on("connect_error", () => {
            popup("websocket offline", "darkred");
        });

        socket.on("disconnect", (reason) => {
            popup("disconnected: " + reason, "darkred");
        });
    }

    return (
        <div
            style={{ backgroundColor: status?.color }}
            className="status"
            hidden={!visible}
        >
            Connection status: {status?.text}
        </div>
    );
}

export default ConnectionStatus;
