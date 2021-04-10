import { io } from "socket.io-client";

let socket = undefined;

function initSocket() {
  if (socket !== undefined) {
    return;
  }

  console.debug("Initializing socket");
  socket = io("http://shove.cc:777", {
    timeout: 1000,
  });
}

function sendPacket(model, packet) {
  if (socket?.connected) {
    socket.send(model, packet);
    console.debug("Sent", model, packet);
    return;
  }

  console.debug("Did not send packet, socket not connected");
}

export { initSocket, sendPacket, socket };
