import { useState } from "react";

import { socket } from "../connection";

let deaf = true;

function ConnectionStatus() {
    const [status, setStatus] = useState("Ready to connect");
    const [sid, setSid] = useState();

    if (deaf) {
        deaf = false;

        socket.on("connect", () => {
            console.debug("> ConnectionStatus connect event");
            setStatus("Connected!");
        });
        socket.on("connect_error", () => {
            console.debug("> ConnectionStatus connect_error event");
            setStatus("Error on connect, backend offline?");
        });
        socket.on("disconnect", (reason) => {
            console.debug("> ConnectionStatus disconnected event", reason);
            setStatus("Disconnected! " + reason);
        });

        socket.on("client_connected", (packet) => {
            console.debug("> ConnectionStatus client_connected", packet);
            if (packet["you"]) {
                setSid(packet["sid"]);
            }
        });
    }

    return (
        <div className="website-status">
            Connection status: {status}
            <br />
            Your sid: {sid}
            <br />
            <br />
        </div>
    );
}

export default ConnectionStatus;
