from convenience import *


class PacketSenderThread(threading.Thread):
    def __init__(self, shove, socketio):
        super().__init__(name="PacketSender", daemon=True)
        self.shove = shove
        self.socketio = socketio

    def run(self):
        Log.trace("Ready")
        send_packets(self.shove, self.socketio)


def send_packets(shove, socketio, loop=True):
    executed = False

    while True:
        if not loop:
            if executed:
                break

            executed = True

        clients, packet, is_response = shove.outgoing_packets_queue.get()

        try:
            _send(socketio, clients, packet, is_response)

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on sending packet", ex)
            continue


def _send(socketio, clients, packet: dict, is_response: bool):
    Log.trace(f"Sending {'response ' if is_response else ''}packet to {clients}: {str(packet)[:200]}")

    sids = [client.sid for client in clients]
    for sid in sids:
        socketio.emit("message", packet, room=sid)

    Log.debug(f"Sent {packet['model']} {'response ' if is_response else ''}packet")
