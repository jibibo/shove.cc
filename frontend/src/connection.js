import { io } from "socket.io-client";

const { REACT_APP_BACKEND_URL } = process.env;
let socket = undefined;

function initSocket() {
  if (socket !== undefined) {
    return;
  }

  console.debug(`Initializing socket, backend url: ${REACT_APP_BACKEND_URL}`);
  socket = io(REACT_APP_BACKEND_URL, {
    timeout: 1000,
  });
}

function sendPacket(model, packet) {
  if (socket?.connected) {
    socket.send(model, packet);
    console.debug("Sent", model, packet);
    return;
  }

  console.warn("Did not send packet, socket not connected");
}

export { initSocket, sendPacket, socket };
