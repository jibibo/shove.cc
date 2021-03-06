import { io } from "socket.io-client";

let socket = undefined;

function initSocket() {
    if (socket !== undefined) {
        return;
    }

    console.debug("Initializing socket");
    socket = io("shove.cc:777", {
        timeout: 1000,
    });
}

function sendPacket(model, packet) {
    if (socket === undefined) {
        console.warn(
            "Tried to send packet with no connection: " + model,
            packet
        );
        return;
    }

    socket.send(model, packet);
    console.debug("Sent packet: " + model, JSON.stringify(packet));
}

export { initSocket, sendPacket, socket };
