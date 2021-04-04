from convenience import *

from shove import Shove
from user import User
from process_audio import ProcessYoutubeThread, process_youtube_wrapper, simulate_processing


class PacketHandlerThread(threading.Thread):
    """This thread handles one received packet at a time"""

    def __init__(self, shove):
        super().__init__(name=f"PHand", daemon=True)
        self.shove = shove

    def run(self):
        Log.trace("Ready")
        handle_packets_loop(self.shove)


def handle_packets_loop(shove):
    while True:
        user, model, packet, packet_number = shove.incoming_packets_queue.get()
        threading.current_thread().setName(f"PHand/#{packet_number}")
        Log.trace(f"Handling packet #{packet_number}")

        try:
            response = handle_packet(shove, user, model, packet)

        except PacketHandlingFailed as ex:
            Log.trace(f"Packet handling failed: {type(ex).__name__}: {ex.description}")
            response = "error", {
                "error": ex.error,
                "description": ex.description
            }

        # todo command handling should throw a CommandHandlingFailed exception

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on packet_handler.handle_packet", ex)
            response = "error", {
                "error": "unhandled_exception",
                "description": "Unhandled backend exception on handling packet (not good)"
            }

        if response:
            response_model, response_packet = response
            Log.trace(f"Handled packet #{packet_number}, response model: '{response_model}'")
            shove.send_packet(user, response_model, response_packet, is_response=True)

        else:
            Log.trace(f"Handled packet #{packet_number}, no response")


def handle_packet(shove: Shove, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
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

    if model == "get_audio":
        return "play_audio", {
            "author": "idk",
            "url": shove.latest_audio
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
        shove.send_packet_all_online("message", {
            "author": username,
            "text": message
        })
        return

    raise PacketInvalid(f"Unknown packet model: '{model}'")


COMMAND_ALIASES = {
    "error": [],
    "help": [],
    "money": ["cash"],
    "play": ["audio"],
    "trello": [],
    "youtube": ["yt"],
}


def is_command(input_str, match_command):
    return input_str == match_command or input_str in COMMAND_ALIASES[match_command]


def handle_command(shove: Shove, user: User, message: str) -> Optional[str]:
    Log.trace(f"Handling command message: '{message}'")
    _command_full_real = message[1:].strip()  # ignore the leading "/"
    _command_full = _command_full_real.lower()
    _command_split_real = _command_full_real.split()
    _command_split = _command_full.split()
    command = _command_split[0] if _command_split else None
    command_args = _command_split[1:] if len(_command_split) > 1 else []  # /command [arg0, arg1, ...]
    command_args_real = _command_split_real[1:] if len(_command_split) > 1 else []

    if not command or is_command(command, "help"):
        return f"{[c for c in COMMAND_ALIASES]}"

    if is_command(command, "error"):  # raises an error to test error handling and logging
        raise Exception("/error was executed, all good")

    if is_command(command, "money"):
        if not user.is_logged_in():
            raise UserNotLoggedIn

        user.get_account()["money"] += 9e15
        shove.send_packet(user, "account_data", user.get_account_data_copy())
        return "Money added"

    if is_command(command, "trello"):
        if not PRIVATE_ACCESS:  # if backend host doesn't have access to the Shove Trello account
            raise NoPrivateAccess

        splitter = "..."
        trello_args = " ".join(command_args_real).split(splitter)
        if len(trello_args) == 1:
            name, description = trello_args[0], None

        elif len(trello_args) == 2:
            name, description = trello_args

        else:
            raise CommandInvalid(f"Invalid arguments: /trello <title> ['{splitter}' description]")

        if not name:
            raise CommandInvalid(f"No card name: /trello <title> ['{splitter}' description]")

        shove.add_trello_card(name, description)
        return "Card added"

    if is_command(command, "play"):
        if not command_args:
            raise CommandInvalid("No link provided")

        check_for_id = command_args_real[0]

        # first check if playlist is given, then queue all of those
        parsed = urlparse.urlparse(check_for_id)
        if "list" in urlparse.parse_qs(parsed.query):
            playlist_id = urlparse.parse_qs(parsed.query)["list"][0]
            max_results = 5  # max 50
            url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults={min(max_results, 50)}&playlistId={playlist_id}&key={YOUTUBE_API_KEY}"
            Log.trace(f"Requesting playlist items from YT API (requesting {max_results}, max 50)")
            response = requests.get(url, timeout=5).json()

            if not response:
                raise PacketHandlingFailed("YT API request broke")

            Log.trace(f"Got response from YT API, items in playlist: {len(response['items'])}")
            youtube_ids = []
            for item in response["items"]:
                youtube_ids.append(item["snippet"]["resourceId"]["videoId"])

            if not youtube_ids:
                raise CommandInvalid("No videos found in given playlist")

        # check if user just dropped the 11-char YT id
        elif len(check_for_id) == 11:
            youtube_ids = [check_for_id]
            Log.trace(f"Got YouTube ID directly: {youtube_ids}")

        # regex magic to find the id in some url
        else:
            match = re.search(r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})", check_for_id)
            if not match:
                raise CommandInvalid("Couldn't find the video ID in given link")

            youtube_ids = [match.group("id")]
            Log.trace(f"Got YouTube ID through regex: {youtube_ids}")

        # ProcessYoutubeThread(shove, youtube_id).start()
        # shove.sio.start_background_task(simulate_processing, 5)
        shove.sio.start_background_task(process_youtube_wrapper, shove, youtube_ids)

        return "Success"

    if is_command(command, "youtube"):
        raise PacketNotImplemented  # disable command

        # if not command_args:
        #     raise CommandInvalid("No link given")
        #
        # check_for_id = command_args_real[0]
        # if len(check_for_id) == 11:
        #     youtube_id = check_for_id
        #     Log.trace(f"Got YouTube ID directly: {youtube_id}")
        # else:
        #     match = re.search(r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})", check_for_id)
        #     if not match:
        #         raise CommandInvalid("Couldn't find the video ID in given link")
        #
        #     youtube_id = match.group("id")
        #     Log.trace(f"Got YouTube ID through regex: {youtube_id}")
        #
        # content_url = f"https://www.googleapis.com/youtube/v3/videos?key=AIzaSyBJhGWLfUiiGydCuKOM06GaR5Tw3sUJW14&id=TnCINj0Miy0&part=snippet,contentDetails,statistics,status"
        # # todo get request takes really long time?
        # # content_url = "https://www.google.com"
        # Log.trace("Fetching video info from Google API")
        # response = requests.get(content_url, stream=True, timeout=1)
        # Log.trace("GET done")
        # Log.test(response.json())
        #
        # shove.send_packet_all_online("youtube", {
        #     "author": user.get_username(),
        #     "id": youtube_id
        # })
        # return "matches"

    raise CommandInvalid(f"Unknown command: '{command}'")

