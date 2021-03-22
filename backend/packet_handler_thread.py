from convenience import *
from user import User
from shove import Shove

try:
    from test import API_KEY, API_SECRET, TOKEN
except ImportError:
    Log.error("Could not import Trello API credentials")
    API_KEY = API_SECRET = TOKEN = None


class CommandFailed(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


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

            except CommandFailed as ex:
                Log.trace(f"Command failed: {ex}")
                response = "command_status", {
                    "success": False,
                    "reason": str(ex)
                }

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
        if "username" in packet:
            username = packet["username"]

        elif user.account:
            username = user.account["username"]

        else:
            return "get_account_data_status", {
                "success": False,
                "reason": "No username given and not signed in"
            }

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
            command = content[1:].strip()
            Log.trace(f"Command: {command}")
            command_lower = command.lower()
            command_split = command_lower.split()

            if command_split[0] == "money":
                user.account["money"] += 9e15
                return "command_status", {
                    "success": True,
                    "command": "money"
                }

            if command_split[0] == "trello":
                Log.trace("Adding card to Trello API list")

                trello_args = " ".join(command_split[1:])
                trello_args_split = trello_args.split("//")
                if len(trello_args_split) == 1:
                    name, desc = trello_args_split[0], None

                elif len(trello_args_split) == 2:
                    name, desc = trello_args_split
                    desc = desc.strip()

                else:
                    raise CommandFailed("Invalid arguments")

                name = name.strip()  # desc is already stripped, or None if it wasn't provided

                client = TrelloClient(  # todo shouldn't be called every time, set as shove.trello_client
                    api_key=API_KEY,
                    api_secret=API_SECRET,
                    token=TOKEN
                )

                board = client.get_board("603c469a39b5466c51c3a176")  # todo shouldn't be called every time
                card_list = board.get_list("60587b1f02721f0c7b547f5b")  # todo shouldn't be called every time
                card_list.add_card(name=name, desc=desc, position="top")
                Log.trace(f"Added card to Trello API list, name = {name}, desc = {desc}")

                return "command_status", {
                    "success": True,
                    "command": "trello"
                }

            raise CommandFailed("Unknown command")

        else:  # not a command, but a chat message
            username = user.account["username"]
            Log.trace(f"Chat message from {username}: {content}")
            shove.send_packet(shove.get_all_users(), "chat_message", {
                "username": username,
                "content": content
            })
            return

    raise InvalidPacket(f"Unknown (or incomplete handler for) packet model: '{model}'")

