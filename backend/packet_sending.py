from convenience import *


class PacketSendingThread(threading.Thread):
    def __init__(self, shove, socketio):
        super().__init__(name="PacketSending", daemon=True)
        self.shove = shove
        self.socketio = socketio

    def run(self):
        Log.trace("Ready")

        while True:
            clients, packet, is_response = self.shove.outgoing_packets_queue.get()

            try:
                _send_packet(self.socketio, clients, packet, is_response)

            except BaseException as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on sending packet", ex)
                continue


def _send_packet(socketio, clients, packet: dict, is_response: bool):
    Log.trace(f"Sending {'response' if is_response else 'packet'} to {clients}: {packet}")

    sids = [client.sid for client in clients]
    for sid in sids:
        socketio.emit("message", packet, room=sid)

    Log.trace(f"Sent {'response' if is_response else 'packet'} with model: {packet['model']} ")
