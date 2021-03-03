from convenience import *
from client import Client
from shove import Shove


class PacketHandlerThread(threading.Thread):
    def __init__(self, shove):
        super().__init__(name=f"PacketHandler", daemon=True)
        self.shove: Shove = shove

    def run(self):
        Log.trace("Ready")
        handle_packets(self.shove)


def handle_packets(shove, loop=True):
    executed = False

    while True:
        if not loop:
            if executed:
                break

            executed = True

        client, packet = shove.incoming_packets_queue.get()

        try:
            response_packet = _handle(shove, client, packet)

        except InvalidPacket as ex:
            Log.error(f"Invalid packet: {ex}", ex)
            continue

        except BaseException as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on handling packet", ex)
            continue

        else:
            if response_packet:
                shove.send_queue(client, response_packet, is_response=True)


def _handle(shove: Shove, client: Client, packet: dict) -> Optional[dict]:
    """Handles the packet and returns an optional response packet"""

    Log.trace(f"Handling packet from {client}: {packet}")

    if not packet:
        raise InvalidPacket("Packet has no information")
    if "model" not in packet:
        raise InvalidPacket("Packet has no model set")
    model = packet["model"]

    if model == "hello":
        return {
            "model": "bye",
            "bye": "jc"
        }

    if model == "get_rooms":
        if "name" in packet["properties"]:
            names = shove.get_all_room_names()

            return {
                "model": "room_list",
                "rooms": [{"name": name} for name in names]
            }

    if model == "join_room":
        room_name = packet["room_name"]
        room = shove.get_room(room_name)

        if room:
            # room.add_player()
            return {
                "model": "join_room_status",
                "success": True,
                "room_name": room_name,
            }

        return {
            "model": "join_room_status",
            "success": False,
            "reason": "enter reason here",
            "room_name": room_name
        }

    if model == "log_in":
        username = packet["username"]
        password = packet["password"]

        return {
            "model": "log_in_status",
            "success": False,
            "reason": "enter reason here",
            "username": username
        }

    if model == "message":
        Log.info(f"Message from {packet['username']}: {packet['content']}")
        shove.send_queue(shove.get_all_clients(), {
            "model": "message",
            "username": packet["username"],
            "content": packet["content"]
        })
        return

    if model == "register":
        username = packet["username"]
        password = packet["password"]

        return {
            "model": "register_status",
            "success": False,
            "reason": "bad",
            "username": username
        }

    raise InvalidPacket(f"Failed handling packet model: {packet['model']}")

