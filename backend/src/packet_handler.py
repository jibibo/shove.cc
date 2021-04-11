from convenience import *

from shove import Shove
from user import User
from commands import handle_command


def handle_packets_loop(shove):
    """Blocking loop for handling packets (that were added to the queue)"""

    set_greenthread_name("PacketHandler")
    Log.trace("Handle packets loop ready")

    while True:
        user, model, packet, packet_id = shove.incoming_packets_queue.get()
        set_greenthread_name(f"PacketHandler/#{packet_id}")
        Log.debug(f"Handling packet #{packet_id}: '{model}'\n packet: {packet}")

        try:
            direct_response = handle_packet(shove, user, model, packet)

        except CommandFailed as ex:
            Log.trace(f"Command invalid: {ex.description}")
            direct_response = "error", {
                "description": ex.description
            }

        except PacketHandlingFailed as ex:
            Log.trace(f"Packet handling failed: {type(ex).__name__}: {ex.description}")  # ex.__name__ as PacketHandlingFailed has children
            direct_response = "error", {
                "description": ex.description
            }

        except NotImplementedError as ex:
            Log.error("Not implemented", ex)
            direct_response = "error", {
                "description": "Not implemented (yet)!"
            }

        except Exception as ex:
            # note: if user purposely sends broken packets, KeyErrors will end up here aswell
            Log.fatal(f"UNHANDLED {type(ex).__name__} on handle_packet", ex)
            direct_response = "error", error_packet(description="Unhandled exception on handling packet (shouldn't happen)")

        if direct_response:
            response_model, response_packet = direct_response
            response_packet_id = shove.get_next_packet_id()
            Log.trace(f"Handled packet, direct response packet is #{response_packet_id}")
            shove.outgoing_packets_queue.put((user, response_model, response_packet, None, response_packet_id))

        else:
            Log.trace(f"Handled packet, no direct response")


def handle_packet(shove: Shove, user: User, model: str, packet: dict) -> Optional[Tuple[str, Union[dict, list]]]:
    """Handles the packet and returns an optional DIRECT response model + packet"""

    if not model:
        raise ValueError("No model provided")

    # if packet was missing from the socketio message, it is None by default
    if packet is None:
        packet = {}  # if no packet provided, just pass on an empty dict to prevent None.getattribute errors

    if type(packet) is not dict:
        raise ValueError(f"Invalid packet type: {type(packet).__name__}")

    if model == "error":  # only errors that should NEVER happen are to be sent to backend (not errors like log in failure)
        Log.error(f"User received a severe error: {packet['description']}")
        return

    # special game packet, should be handled by game's packet handler
    if model == "game_action":  # currently the only model for game packets
        if not user.is_logged_in():
            raise UserNotLoggedIn

        room = shove.get_room_of_user(user)

        if not room:
            raise UserNotInRoom

        if not room.game:
            raise GameNotSet

        response = room.game.handle_packet(user, model, packet)  # can return a response (model, packet) tuple
        return response

    if model == "get_account_data":
        if "username" in packet:
            username = packet["username"].strip()
            account = shove.accounts.find_single(match_casing=False, username=username)

        elif user.is_logged_in():
            account = user.get_account()

        else:
            raise UserNotLoggedIn

        return "account_data", account.get_json_serializable()

    if model == "get_account_list":
        return "account_list", shove.accounts.get_entries_data_sorted(key=lambda e: e["username"])

    if model == "get_game_data":
        room = shove.get_room_of_user(user)

        if not room:
            raise UserNotInRoom

        if not room.game:
            raise GameNotSet

        return "game_data", room.game.get_data()

    if model == "get_room_data":
        raise NotImplementedError

    if model == "get_room_list":
        return "room_list", [room.get_data() for room in shove.get_rooms()]

    if model == "get_song_rating":
        if not shove.latest_song:
            Log.trace("No song playing, ignoring")
            return

        return "song_rating", shove.latest_song.get_rating_of(user)

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
        account = shove.accounts.find_single(username=username)

        if account["password"] != password:
            # raise PasswordInvalid  # comment out to disable password checking
            pass

        user.log_in_as(account)

        return "log_in", {
            "account_data": user.get_account_data_copy()
        }

    if model == "log_out":
        if not user.is_logged_in():
            raise UserNotLoggedIn

        shove.log_out_user(user)

        return

    if model == "play_song":
        category = packet["category"]

        if category == "popular":
            eligible = set()
            # if a song has a good enough likes/(likes+dislikes)) ratio, it is "popular"
            for song in shove.songs.get_entries():
                if song.is_popular():
                    eligible.add(song)

        elif category == "random":
            eligible = shove.songs.get_entries()

        else:
            raise ActionInvalid(f"Invalid song category provided: {category}")

        Log.trace(f"Eligible songs count: {len(eligible)}")
        if not eligible:
            raise NoSongsAvailable

        song = random.choice(list(eligible))
        Log.trace(f"Picked song to play: {song}")
        song.play(shove, user)
        return

    if model == "pong":
        now = time.time()
        user.latency = now - user.pinged_timestamp
        user.last_pong_received = now
        Log.trace(f"Pong received from {user} ({user.pinged_timestamp}), latency: {round(user.latency * 1000)} ms")

        return "latency", {
            "latency": user.latency
        }

    if model == "rate_song":
        if not user.is_logged_in():
            raise UserNotLoggedIn

        song = shove.latest_song
        if not song:
            raise NoSongPlaying

        username = user.get_username()
        action = packet["action"]

        if action == "toggle_dislike":
            song.toggle_dislike(username)
        elif action == "toggle_like":
            song.toggle_like(username)
        else:
            raise ActionInvalid

        song.broadcast_rating(shove)

        return

    if model == "register":
        raise NotImplementedError

    if model == "send_message":
        message: str = packet["message"].strip()

        if not message:
            Log.trace("Empty message provided, ignoring")
            return

        # check if message is a command first, as some commands don't require user to be logged in
        if message.startswith("/"):
            response_message = handle_command(shove, user, message)  # returns optional response message to user
            return "command_success", {
                "response": response_message
            }

        # not a command, so it is a chat message
        if not user.is_logged_in():
            raise UserNotLoggedIn

        username = user.get_username()
        Log.trace(f"Message from {username}: '{message}'")
        shove.send_packet_to_everyone("message", {
            "author": username,
            "text": message
        })
        return

    raise ModelInvalid
