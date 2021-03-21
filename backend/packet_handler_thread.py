from convenience import *
from user import User
from shove import Shove


class InvalidPacket(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class PacketHandlerThread(threading.Thread):
    """This thread gets created and run to handle one received packet at a time"""

    def __init__(self, shove):
        super().__init__(name=f"PacketHandler", daemon=True)
        self.shove: Shove = shove

    def run(self):
        Log.trace("Ready")

        while True:
            user, model, packet, packet_number = self.shove.incoming_packets_queue.get()
            threading.current_thread().setName(f"PacketHandler/#{packet_number}")
            Log.trace(f"Handling packet #{packet_number}")

            try:
                response = handle_packet(self.shove, user, model, packet)

            except InvalidPacket as ex:
                Log.error(f"Invalid packet: {ex}")
                response = "error", {
                    "error": "invalid_packet",
                    "description": "Invalid packet sent by user (frontend error)"
                }

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on handle_packet", ex)
                response = "error", {
                    "error": "unhandled_exception",
                    "description": "An unhandled exception occurred in the backend on handling the packet"
                }

            if response:
                response_model, response_packet = response
                Log.trace(f"Handled packet #{packet_number}, response model: '{response_model}'")
                self.shove.send_packet(user, response_model, response_packet, is_response=True)

            else:
                Log.trace(f"Handled packet #{packet_number}, no response")


def handle_packet(shove: Shove, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
    """Handles the packet and returns an optional response model + packet"""

    if not model:
        raise InvalidPacket("No model provided")
    if type(packet) != dict:
        raise InvalidPacket(f"Packet type invalid: {type(packet).__name__}")

    # special game packet, should be handled by game's packet handler
    if model.startswith("game"):
        room = shove.get_room_of_user(user)
        if room and room.game:
            response = room.game.handle_packet(user, model, packet)
            if response:
                model, packet = response
                return model, packet

    if model == "get_account_data":
        try:
            username = packet["username"]
        except KeyError:
            username = user.account["username"]  # todo user can possibly be not logged in, potential error

        account = shove.get_account(username=username)

        if account:
            data = account.data.copy()
            del data["password"]  # remove password from account data

            return "get_account_data_status", {
                "success": True,
                "data": data
            }

        else:
            return "get_account_data_status", {
                "success": False,
                "reason": "User not found"
            }

    if model == "get_room_list":
        if "name" in packet["properties"]:
            room_list = []
            for room in shove.get_rooms():
                room_list_entry = {
                    "name": room.name,
                    "user_count": room.get_user_count(),
                    "max_user_count": "∞"
                }
                room_list.append(room_list_entry)

            return "room_list", {
                "room_list": room_list
            }

    if model == "join_room":
        if not user.account:
            return "join_room_status", {
                "success": False,
                "reason": "Not logged in",
            }

        room_name = packet["room_name"]
        room = shove.get_room(room_name)

        if room:
            fail_reason = room.user_tries_to_join(user)

            if fail_reason:
                Log.trace(f"{user} could not join {room}, reason: {fail_reason}")
                return "join_room_status", {
                    "success": False,
                    "reason": fail_reason,
                }

            else:
                Log.info(f"{user} joined room {room}")
                return "join_room_status", {
                    "success": True,
                    "room_name": room_name,
                }

        else:
            return "join_room_status", {
                "success": False,
                "reason": "Room not found",
            }

    if model == "leave_room":
        Log.warn("not implemented")
        return

    if model == "log_in":
        username = packet["username"]
        # password = packet["password"]  # todo matching password check
        account = shove.get_account(username=username)

        if account:
            user.log_in(account)
            return "log_in_status", {
                "success": True,
                "username": username
            }

        return "log_in_status", {
            "success": False,
            "reason": "User not found"
        }

    if model == "register":
        # username = packet["username"]
        # password = packet["password"]
        Log.warn("not implemented")

        return "register_status", {
            "success": False,
            "reason": "Not implemented"
        }

    if model == "send_message":
        content: str = packet["content"].strip()

        if not content:
            Log.trace("No message content, ignoring")
            return

        if content.startswith("/"):
            command = content[1:].strip().lower()
            Log.trace(f"Command: {command}")

            if command == "money":
                user.account["money"] += 9e15
                return "command_status", {
                    "success": True
                }

            return "command_status", {
                "success": False,
                "reason": f"Invalid command: {command}"
            }

        username = user.account["username"]
        Log.trace(f"Chat message from {username}: {content}")
        shove.send_packet(shove.get_all_users(), "chat_message", {
            "username": username,
            "content": content
        })
        return

    raise InvalidPacket(f"Unknown (or incomplete handler for) packet model: '{model}'")

