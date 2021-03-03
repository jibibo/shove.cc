from util import *
from client import Client


class PacketHandlerThread(threading.Thread):
    def __init__(self, server):
        super().__init__(name=f"PacketHandler", daemon=True)
        self.server = server

    def run(self):
        Log.trace("Running")
        handle_packets(self.server, loop=True)


def handle_packets(server, loop=False):
    executed = False

    while True:
        if not loop:
            if executed:
                break

            executed = True

        client, packet = server.incoming_packets_queue.get()

        try:
            response_packet = _handle(server, client, packet)

            if response_packet:
                server.send_packet(client, response_packet, is_response=True)

        except InvalidPacket as ex:
            Log.error(f"Invalid packet: {ex}", ex)
            continue

        except BaseException as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on handling packet", ex)
            continue


def _handle(server, client: Client, packet: dict) -> Optional[dict]:
    """Handles the packet and returns a response packet, or None"""

    Log.trace(f"Handling packet from {client}: {packet}")

    if not packet:
        raise InvalidPacket("packet has no information")
    if "model" not in packet:
        raise InvalidPacket("packet has no model set")
    model = packet["model"]

    if model == "message":
        Log.info(f"Message from {packet['username']}: {packet['message']}")
        server.send_packet(server.get_all_clients(), {
            "model": "message",
            "username": packet["username"],
            "message": packet["message"]
        })
        return

    if model == "room_join":
        # try:
        #     ROOM_SIDS[packet["room"]].append(sender_sid)
        #
        # except KeyError:
        #     return {
        #         "model": "room_joined_status",
        #         "success": False
        #     }
        #
        # Log.info(f"{sender_sid} joined room {packet['room']}")
        # send_packet(ROOM_SIDS[packet["room"]], {
        #     "model": "room_joined_someone",
        #     "username": sender_sid
        # }, sender_sid)

        return {
            "model": "room_joined_status",
            "success": False
        }

    raise InvalidPacket(f"unknown packet model: {packet['model']}")

