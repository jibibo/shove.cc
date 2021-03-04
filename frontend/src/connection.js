import { io } from "socket.io-client";
import { addMessage } from "./components/MessageBox";
import handlePacket from "./handlePacket";

let socket = undefined;

function initSocket() {
    if (socket !== undefined) {
        return;
    }

    console.log("Initializing socket");

    socket = io.connect(document.domain + ":777");

    socket.on("message", (packet) => {
        handlePacket(packet);
    });
    socket.on("connect", () => {
        addMessage("Connection established", "green");
    });
    socket.on("connect_error", () => {
        addMessage("Failed to connect, socket offline?", "red");
    });
    socket.on("disconnect", (reason) => {
        addMessage("Connection lost: " + reason, "red");
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

export { initSocket, sendPacket };
