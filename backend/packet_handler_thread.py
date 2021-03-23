from convenience import *
from user import User
from shove import Shove

try:
    from test import API_KEY, API_SECRET, TOKEN
except ImportError:
    Log.error("Could not import Trello API credentials")
    API_KEY = API_SECRET = TOKEN = None


class PacketHandlerThread(threading.Thread):
    """This thread handles one received packet at a time"""

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
                response = handle_incoming_packet(self.shove, user, model, packet)

            except PacketHandlingError as ex:
                Log.trace(f"Packet handling error: {ex.error}: {ex.description}")
                response = "error", {
                    "error": ex.error,
                    "description": ex.description
                }

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on handle_incoming_packet", ex)
                response = "error", {
                    "error": "unhandled_exception",
                    "description": "Unhandled exception in backend (not good)"
                }

            if response:
                response_model, response_packet = response
                Log.trace(f"Handled packet #{packet_number}, response model: '{response_model}'")
                self.shove.send_packet(user, response_model, response_packet, is_response=True)

            else:
                Log.trace(f"Handled packet #{packet_number}, no response")


# todo instead of "success": False status packets, give a proper error (unauthorized/invalid command/etc)
def handle_incoming_packet(shove: Shove, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
    """Handles the packet and returns an optional response model + packet"""

    if not model:
        raise PacketInvalid("No model provided")

    if type(packet) != dict:
        raise PacketInvalid(f"Invalid packet type: {type(packet).__name__}")

    if model == "get_account_data":
        if "username" in packet:
            username = packet["username"]

        elif user.account:
            username = user.account["username"]

        else:
            raise PacketInvalid("Not logged in and no username provided")

        account = shove.get_account(username=username)

        account_data = account.get_data()

        return "account_data", {
            "account_data": account_data
        }

    if model == "get_game_state":
        room = shove.get_room_of_user(user)

        if not room:
            raise PacketInvalid("Not in a room")

        if not room.game:
            raise GameNotSet

        return "game_state", room.game.get_state_packet()

    if model == "get_room_list":  # send a list of dicts with each room's data
        return "room_list", {
            "room_list": [room.get_data() for room in shove.get_rooms()]
        }

    if model == "leave_room":
        raise PacketNotImplemented

    # special game packet, should be handled by game's packet handler
    if model == "try_game_action":  # currently the only model for game packets
        room = shove.get_room_of_user(user)

        if not room:
            raise PacketInvalid("Not in a room")

        if not room.game:
            raise GameNotSet

        response = room.game.handle_packet(user, model, packet)  # optionally returns a response (model, packet) tuple
        return response

    if model == "try_join_room":
        if not user.account:
            raise PacketUserUnauthorized("Not logged in")

        room_name = packet["room_name"]
        room = shove.get_room(room_name)

        if not room:
            raise RoomNotFound

        room.user_tries_to_join(user)  # this throws an exception if user can't join room

        return "join_room", {
            "room_name": room_name,
        }

    if model == "try_log_in":
        username = packet["username"]
        # password = packet["password"]  # todo matching password check
        account = shove.get_account(username=username)

        user.log_in(account)

        account_data = account.get_data()

        return "log_in", {
            "account_data": account_data
        }

    if model == "try_register":
        raise PacketNotImplemented

    if model == "try_send_message":
        message: str = packet["message"].strip()

        if not message:
            Log.trace("Empty message, ignoring")
            return

        if message.startswith("/"):
            response_message = handle_command(shove, user, message)  # returns optional response message to user
            return "command_success", {
                "message": response_message
            }

        # not a command, so it is a chat message
        if not user.account:
            raise PacketUserUnauthorized("Not logged in")

        username = user.account["username"]
        Log.trace(f"Chat message from {username}: '{message}'")
        shove.send_packet(shove.get_all_users(), "message", {
            "username": username,
            "message": message
        })
        return

    raise PacketInvalid(f"Unknown packet model: '{model}'")


def handle_command(shove: Shove, user: User, message: str) -> Optional[str]:
    Log.trace(f"Handling command: '{message}'")
    command = message[1:].strip()
    command_lower = command.lower()
    command_split = command_lower.split()

    if command_lower == "money":
        user.account["money"] += 9e15
        return "Money added"

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
            raise PacketCommandInvalid("Invalid arguments")

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
        return

    raise PacketCommandInvalid(f"Unknown command: '{command_lower}'")
