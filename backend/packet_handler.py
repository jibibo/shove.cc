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

    def __init__(self, shove, client, model, packet, packet_number):
        super().__init__(name=f"PacketHandler/{packet_number}", daemon=True)
        self.shove: Shove = shove
        self.client = client
        self.model = model
        self.packet = packet

    def run(self):
        Log.trace(f"Handling {self.model} packet from {self.client}: {self.packet}")

        try:
            response = _handle_packet(self.shove, self.client, self.model, self.packet)

        except InvalidPacket as ex:
            Log.error(f"Invalid packet: {ex}", ex)
            return

        except BaseException as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} caught", ex)
            return

        if response:
            model, packet = response
            self.shove.send_queue(self.client, model, packet, is_response=True)


def _handle_packet(shove: Shove, client: Client, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
    """Handles the packet and returns an optional response packet dict"""

    if not model:
        raise InvalidPacket("No model provided")
    if not packet:
        raise InvalidPacket("Packet is empty")

    if model == "chat_message":
        Log.info(f"Message from {packet['username']}: {packet['content']}")
        shove.send_queue(shove.get_all_clients(), "chat_message", {
            "username": packet["username"],
            "content": packet["content"]
        })
        return

    if model == "hello":
        return "bye", {
            "bye": "jc"
        }

    if model == "get_rooms":
        if "name" in packet["properties"]:
            names = shove.get_all_room_names()

            return "room_list", {
                "rooms": [{"name": name} for name in names]
            }

    if model == "join_room":
        # # temporary
        # username = packet["room_name"]
        # account_data = shove.get_account_data(username=username)
        # Log.test(f"match {account_data}")

        # original
        room_name = packet["room_name"]
        room = shove.get_room(room_name)

        if room:
            # room.add_player()
            return "join_room_status", {
                "success": True,
                "room_name": room_name,
            }

        return "join_room_status", {
            "success": False,
            "reason": "enter reason here",
            "room_name": room_name
        }

    if model == "log_in":
        username = packet["username"]
        password = packet["password"]

        return "log_in_status", {
            "success": False,
            "reason": "enter reason here",
            "username": username
        }

    if model == "register":
        username = packet["username"]
        password = packet["password"]

        return "register_status", {
            "success": False,
            "reason": "bad",
            "username": username
        }

    raise InvalidPacket(f"Failed handling packet with model: {packet['model']}")

