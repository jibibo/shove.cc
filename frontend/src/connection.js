import { useContext } from "react";
import { io } from "socket.io-client";
import handlePacket from "./handlePacket";

import { GlobalContext } from "./components/GlobalContext";

let socket = undefined;

function InitSocket() {
    const { messages, setMessages } = useContext(GlobalContext);

    console.debug("Initializing socket");

    if (socket !== undefined) {
        console.debug("Socket already initialized, ignoring call");
        return;
    }

    socket = io.connect(document.domain + ":777");

    socket.on("message", (packet) => {
        handlePacket(packet);
    });
    socket.on("connect", () => {
        setMessages(messages.concat("Connection established"));
    });
    socket.on("connect_error", () => {
        setMessages(messages.concat("Failed to connect, socket offline?"));
    });
    socket.on("disconnect", (reason) => {
        setMessages(messages.concat("Connection lost: " + reason));
    });
    socket.send({
        model: "get_rooms",
        properties: ["name"],
    });
}

function sendPacket(packet) {
    if (socket === undefined) {
        console.error("Tried to send packet with no connection:", packet);
        return;
    }

    socket.send(packet);
    console.debug("Sent packet:", JSON.stringify(packet));
}

export { InitSocket, sendPacket };
