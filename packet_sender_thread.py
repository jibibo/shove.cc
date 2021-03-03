from util import *


class PacketSenderThread(threading.Thread):
    def __init__(self, server, socketio):
        super().__init__(name="PacketSender", daemon=True)
        self.server = server
        self.socketio = socketio

    def run(self):
        Log.trace("Running")
        send_packets(self.server, self.socketio, loop=True)


def send_packets(server, socketio, loop=False):
    executed = False

    while True:
        if not loop:
            if executed:
                break

            executed = True

        clients, packet, is_response = server.outgoing_packets_queue.get()

        try:
            _send(socketio, clients, packet, is_response)

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on sending packet", ex)
            continue


def _send(socketio, clients, packet: dict, is_response=False):
    Log.trace(f"Sending {'response' if is_response else 'packet'} to {clients}: {packet}")

    sids = [client.sid for client in clients]
    for sid in sids:
        socketio.emit("message", packet, room=sid)

    Log.debug(f"Sent {packet['model']} packet")
