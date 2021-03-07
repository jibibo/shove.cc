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

    def __init__(self, shove):
        super().__init__(name=f"PacketHandler", daemon=True)
        self.shove: Shove = shove

    def run(self):
        Log.trace("Ready")

        while True:
            client, model, packet, packet_number = self.shove.incoming_packets_queue.get()
            threading.current_thread().setName(f"PacketHandler/{packet_number}")
            Log.trace(f"Handling packet #{packet_number}")

            try:
                response = _handle_packet(self.shove, client, model, packet)

            except InvalidPacket as ex:
                Log.error(f"Invalid packet: {ex}", ex)
                continue

            except BaseException as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} caught", ex)
                continue

            model = "нет!"

            if response:
                model, packet = response
                self.shove.send_packet(client, model, packet, is_response=True)

            Log.trace(f"Handled packet #{packet_number}, response: '{model}'")


def _handle_packet(shove: Shove, client: Client, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
    """Handles the packet and returns an optional response packet dict"""

    if not model:
        raise InvalidPacket("no model provided")
    if not packet:
        raise InvalidPacket("packet is empty")

    if model == "chat_message":
        Log.info(f"Message from {packet['username']}: {packet['content']}")
        shove.send_packet(shove.get_all_clients(), "chat_message", {
            "username": packet["username"],
            "content": packet["content"]
        })
        return

    if model == "get_rooms":
        if "name" in packet["properties"]:
            # names = shove.get_all_room_names()
            rooms = []
            for room in shove.rooms:
                room_data = {
                    "name": room.name,
                    "players": len(room.get_taken_seats()),
                    "max_players": room.n_seats
                }
                rooms.append(room_data)

            return "room_list", {
                "rooms": rooms
            }

    if model == "join_room":
        username = packet["username"]
        room_name = packet["room_name"]

        if not username:
            return "join_room_status", {
                "success": True,
                "reason": "not logged in",
                "room_name": room_name
            }

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
        }

    if model == "log_in":
        username = packet["username"]
        password = packet["password"]  # todo matching password check
        account_data = shove.get_account_data(username=username)

        if account_data:
            client.log_in(account_data)
            return "log_in_status", {
                "success": True,
                "username": username
            }

        return "log_in_status", {
            "success": False,
            "reason": "user with username not found",
            "username": username
        }

    if model == "register":
        username = packet["username"]
        password = packet["password"]

        return "register_status", {
            "success": False,
            "reason": "not implemented",
            "username": username
        }

    raise InvalidPacket(f"unknown (or incomplete handler) model: {packet['model']}")

