from convenience import *


class PacketSenderThread(threading.Thread):
    def __init__(self, shove, socketio):
        super().__init__(name="PacketSender", daemon=True)
        self.shove = shove
        self.socketio = socketio

    def run(self):
        Log.trace("Ready")

        while True:
            clients, model, packet, is_response = self.shove.outgoing_packets_queue.get()
            Log.debug(f"Sending {'response' if is_response else 'packet'}: '{model}'\n to: {clients}\n packet: {packet}")

            try:
                send_outgoing_packet(self.socketio, clients, model, packet, is_response)

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on send_outgoing_packet", ex)


def send_outgoing_packet(socketio, clients, model: str, packet: dict, is_response: bool):
    sids = [client.sid for client in clients]
    for sid in sids:
        socketio.emit(model, packet, room=sid)

    Log.trace(f"Sent {'response' if is_response else 'packet'}: '{model}'")
