from convenience import *
from client import Client
from shove import Shove


class InvalidPacket(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class PacketHandlerThread(threading.Thread):
    """This thread gets created and run to handle a single received packet"""

    def __init__(self, shove, client, packet, packet_number):
        super().__init__(name=f"PacketHandler/{packet_number}", daemon=True)
        self.shove: Shove = shove
        self.client = client
        self.packet= packet

    def run(self):
        Log.trace(f"Handling packet from {self.client}: {self.packet}")

        try:
            # response_packet = _handle(shove, client, packet)
            response_packet = _handle_packet(self.shove, self.client, self.packet)

        except InvalidPacket as ex:
            Log.error(f"Invalid packet: {ex}", ex)
            return

        except BaseException as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} caught", ex)
            return

        if response_packet:
            self.shove.send_queue(self.client, response_packet, is_response=True)


def _handle_packet(shove: Shove, client: Client, packet: dict) -> Optional[dict]:
    """Handles the packet and returns an optional response packet dict"""

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
        # temporary
        username = packet["room_name"]
        account_data = shove.get_account_data(username=username)
        Log.test(f"match {account_data}")

        # original
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

    raise InvalidPacket(f"Failed handling packet with model: {packet['model']}")

