from convenience import *
from user import User
from shove import Shove


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


# todo remove try_ from the packets, redundant
def handle_incoming_packet(shove: Shove, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
    """Handles the packet and returns an optional response model + packet"""

    if not model:
        raise PacketInvalid("No model provided")

    if type(packet) != dict:
        raise PacketInvalid(f"Invalid packet type: {type(packet).__name__}")

    # special game packet, should be handled by game's packet handler
    if model == "try_game_action":  # currently the only model for game packets
        room = shove.get_room_of_user(user)

        if not room:
            raise PacketInvalid("Not in a room")

        if not room.game:
            raise GameNotSet

        response = room.game.handle_packet(user, model, packet)  # optionally returns a response (model, packet) tuple
        return response

    if model == "get_account_data":
        if "username" in packet:
            username = packet["username"].strip().lower()
            account = shove.get_account(username=username)

        elif user.account:
            account = user.account

        else:
            raise PacketInvalid("Not logged in and no username provided")

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

        return "game_state", room.game.get_info_packet()

    if model == "get_room_list":  # send a list of dicts with each room's data
        return "room_list", {
            "room_list": [room.get_data() for room in shove.get_rooms()]
        }

    if model == "try_join_room":
        if not user.account:
            raise UserUnauthorized("Not logged in")

        if shove.get_room_of_user(user):
            raise UserAlreadyInRoom

        room = shove.get_room(packet["room_name"])

        if not room:
            raise RoomNotFound

        room.user_tries_to_join(user)  # this throws an exception if user can't join room

        return "join_room", {
            "room_name": room.name,
            "room_data": None,  # todo implement, safes sending 1 packet
            "game_state": None
        }

    if model == "try_leave_room":
        if not user.account:
            raise UserUnauthorized("Not logged in")

        room = shove.get_room_of_user(user)

        if not room:
            raise UserNotInRoom

        room.user_leave(user)

        return "leave_room", {
            "room_name": room.name
        }

    if model == "try_log_in":
        username = packet["username"].strip().lower()
        password = packet["password"]
        account = shove.get_account(username=username)

        if account["password"] != password:
            # raise PasswordInvalid  # comment out to disable password checking
            pass

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
            raise UserUnauthorized("Not logged in")

        username = user.account["username"]
        Log.trace(f"Chat message from {username}: '{message}'")
        shove.send_packet_all("message", {
            "author": username,
            "message": message
        })
        return

    raise PacketInvalid(f"Unknown packet model: '{model}'")


def handle_command(shove: Shove, user: User, message: str) -> Optional[str]:
    Log.trace(f"Handling command: '{message}'")
    command = message[1:].strip().lower()
    command_split = command.split()

    if command == "money":
        user.account["money"] += 9e15
        return "Money added"

    if command_split[0] == "trello":
        trello_args = " ".join(command_split[1:])
        trello_args_split = trello_args.split("//")
        if len(trello_args_split) == 1:
            name, description = trello_args_split[0], None

        elif len(trello_args_split) == 2:
            name, description = trello_args_split

        else:
            raise CommandInvalid("Invalid arguments")

        shove.add_trello_card(name, description)
        return

    raise CommandInvalid(f"Unknown command: '{command}'")
