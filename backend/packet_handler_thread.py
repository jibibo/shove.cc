from convenience import *

from shove import Shove
from user import User


class PacketHandlerThread(threading.Thread):
    """This thread handles one received packet at a time"""

    def __init__(self, shove):
        super().__init__(name=f"PacketHandler", daemon=True)
        self.shove = shove

    def run(self):
        Log.trace("Ready")

        while True:
            user, model, packet, packet_number = self.shove.incoming_packets_queue.get()
            threading.current_thread().setName(f"PacketHandler/#{packet_number}")
            Log.trace(f"Handling packet #{packet_number}")

            try:
                response = handle_incoming_packet(self.shove, user, model, packet)

            except PacketHandlingFailed as ex:
                Log.trace(f"Packet handling failed: {type(ex).__name__}: {ex.description}")
                response = "error", {
                    "error": ex.error,
                    "description": ex.description
                }

            # todo command handling should throw a CommandHandlingFailed exception

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on handle_incoming_packet", ex)
                response = "error", {
                    "error": "unhandled_exception",
                    "description": "Unhandled server exception on handling user packet (not good)"
                }

            if response:
                response_model, response_packet = response
                Log.trace(f"Handled packet #{packet_number}, response model: '{response_model}'")
                self.shove.send_packet(user, response_model, response_packet, is_response=True)

            else:
                Log.trace(f"Handled packet #{packet_number}, no response")


def handle_incoming_packet(shove: Shove, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
    """Handles the packet and returns an optional response model + packet"""

    if not model:
        raise PacketInvalid("No model provided")

    if type(packet) != dict:
        raise PacketInvalid(f"Invalid packet type: {type(packet).__name__}")

    # special game packet, should be handled by game's packet handler
    if model == "game_action":  # currently the only model for game packets
        if not user.is_logged_in():
            raise UserNotLoggedIn

        room = shove.get_room_of_user(user)

        if not room:
            raise PacketInvalid("Not in a room")

        if not room.game:
            raise GameNotSet

        response = room.game.handle_packet(user, model, packet)  # can return a response (model, packet) tuple
        return response

    if model == "get_account_data":
        if "username" in packet:
            username = packet["username"].strip().lower()
            account_data = shove.get_account(username=username).get_data_copy()

        elif user.is_logged_in():
            account_data = user.get_account_data_copy()

        else:
            raise PacketInvalid("Not logged in and no username provided")

        return "account_data", account_data

    if model == "get_account_list":
        return "account_list", {
            "account_list": [account.get_data_copy() for account in shove.get_all_accounts()]
        }

    if model == "get_game_data":
        room = shove.get_room_of_user(user)

        if not room:
            raise PacketInvalid("Not in a room")

        if not room.game:
            raise GameNotSet

        return "game_data", room.game.get_data()

    if model == "get_room_data":
        raise PacketNotImplemented

    if model == "get_room_list":  # send a list of dicts with each room's data
        return "room_list", {
            "room_list": [room.get_data() for room in shove.get_rooms()]
        }

    if model == "join_room":
        if shove.get_room_of_user(user):
            raise UserAlreadyInRoom

        room = shove.get_room(packet["room_name"])

        if not room:
            raise RoomNotFound

        room.user_tries_to_join(user)  # this throws an exception if user can't join room

        if room.game:
            game_data = room.game.get_data()
        else:
            game_data = None

        return "join_room", {
            "room_data": room.get_data(),
            "game_data": game_data
        }

    if model == "leave_room":
        if not user.is_logged_in():
            raise UserNotLoggedIn

        room = shove.get_room_of_user(user)

        if not room:
            raise UserNotInRoom

        room.user_leave(user)

        return "leave_room", {
            "room_name": room.name
        }

    if model == "log_in":
        username = packet["username"].strip().lower()
        password = packet["password"]
        account = shove.get_account(username=username)

        if account["password"] != password:
            # raise PasswordInvalid  # comment out to disable password checking
            pass

        user.log_in(account)

        return "log_in", {
            "account_data": user.get_account_data_copy()
        }

    if model == "log_out":
        if not user.is_logged_in():
            raise UserNotLoggedIn

        room = shove.get_room_of_user(user)

        if room:
            room.user_leave(user)

        user.log_out()

        return "log_out", {}

    if model == "pong":
        now = int(time.time() * 1000)
        user.latency = now - user.pinged_timestamp
        Log.trace(f"Pong received from {user} ({user.pinged_timestamp}), latency: {user.latency} ms")

        if user in shove.awaiting_pong_users:  # just to be sure
            shove.awaiting_pong_users.remove(user)

        else:
            Log.warn(f"User {user} not in shove.awaiting_pong_users?")

        return "latency", {
            "latency": user.latency
        }

    if model == "register":
        raise PacketNotImplemented

    if model == "send_message":
        message: str = packet["message"].strip()

        if not message:
            Log.trace("Empty message, ignoring")
            return

        # check if message is a command, as some commands don't require user to be logged in
        if message.startswith("/"):
            response_message = handle_command(shove, user, message)  # returns optional response message to user
            response = response_message
            return "command_success", {
                "response": response
            }

        # not a command, so it is a chat message
        if not user.is_logged_in():
            raise UserNotLoggedIn

        username = user.get_username()
        Log.trace(f"Message from {username}: '{message}'")
        shove.send_packet_all("message", {
            "author": username,
            "text": message
        })
        return

    raise PacketInvalid(f"Unknown packet model: '{model}'")


def handle_command(shove, user: User, message: str) -> Optional[str]:
    Log.trace(f"Handling command: '{message}'")
    command = message[1:].strip().lower()
    command_split = command.split()

    if not command:
        raise CommandInvalid("'/' doesn't do anything")

    if command == "error":  # raises an error to test error handling and logging
        raise Exception("/error was executed, all good")

    if command == "money":
        if not user.is_logged_in():
            raise UserNotLoggedIn

        user.get_account()["money"] += 9e15
        shove.send_packet(user, "account_data", user.get_account_data_copy())
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

        if not name:
            Log.trace("No card name provided, ignoring")
            return

        shove.add_trello_card(name, description)
        return "Card added"

    if len(command_split) < 2:  # prevent IndexErrors if not enough command arguments
        raise CommandInvalid(f"Unknown command: '{command}'")

    raise CommandInvalid(f"Unknown command: '{command}'")
