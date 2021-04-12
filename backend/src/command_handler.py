from convenience import *

from shove import Shove
from user import User
from process_song import process_song_task

COMMANDS = {
    "account": {
        "aliases": ["a"],
        "usage": "/account <avatar> <url> OR /account <create/delete> <username>"
    },
    "error": {
        "aliases": [],
        "usage": "/error"
    },
    "help": {
        "aliases": ["?"],
        "usage": "/help"
    },
    "money": {
        "aliases": ["cash"],
        "usage": "/money"
    },
    "play": {
        "aliases": ["p", "audio", "music", "song"],
        "usage": "/play <url/ID>"
    },
    "trello": {
        "aliases": ["t"],
        "splitter": "...",
        "usage": "/trello <card name> '...' [card description]"
    }
}


def is_command(command, match_with):
    return command == match_with or command in COMMANDS[match_with]["aliases"]


def handle_command(shove: Shove, user: User, message: str) -> Optional[str]:
    Log.trace(f"Handling command message: '{message}'")
    _message_full_casing = message[1:].strip()  # [1:] -> ignore the leading "/"
    _message_full = _message_full_casing.lower()
    _message_split_casing = _message_full_casing.split()
    _message_split = _message_full.split()
    command = _message_split[0] if _message_split else None
    command_args = _message_split[1:] if len(_message_split) > 1 else []  # /command [arg0, arg1, ...]
    command_args_casing = _message_split_casing[1:] if len(_message_split) > 1 else []

    if not command or is_command(command, "help"):
        return f"{[c for c in COMMANDS.keys()]}"

    if is_command(command, "account"):

        if command_args[0] == "avatar":
            if not user.is_logged_in():
                raise UserNotLoggedIn

            if len(command_args) == 1:
                url = None
            else:
                url = command_args_casing[1]

            if url:
                # todo check file size of the image (>1MB is error)

                Log.trace(f"Sending GET request")
                # https://stackoverflow.com/a/13137873/13216113
                response = requests.get(url, stream=True, timeout=3)
                Log.trace(f"GET response: {response.status_code}")

                if response.status_code != 200:
                    raise CommandFailed(f"Could not access URL, code {response.status_code}")

                valid_mime_types = list(AVATAR_MIME_EXTENSIONS.keys())
                content_type = response.headers["content-type"]
                if content_type not in valid_mime_types:
                    raise CommandFailed(f"Invalid file type, must be one of {valid_mime_types}")

                extension = AVATAR_MIME_EXTENSIONS[content_type]
                # https://stackoverflow.com/a/534847/13216113
                filename = f"{uuid.uuid4().hex}.{extension}"  # create the filename
                file_path = f"{FILES_FOLDER}/{AVATARS_FOLDER}/{filename}"

                with open(file_path, "wb") as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)

                user.get_account()["avatar_type"] = content_type
                user.get_account()["avatar_filename"] = filename
                Log.trace(f"Stored avatar of {user} as {filename}")
                return "Success"

            else:
                Log.trace("Removing avatar")
                # doesn't actually delete the image from disk (yet)
                user.get_account()["avatar_filename"] = None
                user.get_account()["avatar_type"] = None
                return "Unlisted your avatar (not removed from disk)"

        if command_args[0] == "create":
            if len(command_args) == 1:
                preferred_username = None

            elif len(command_args) == 2:
                preferred_username = command_args_casing[1]

            else:
                raise CommandFailed(COMMANDS["account"]["usage"])

            username = shove.accounts.create_random_account(preferred_username)["username"]

            shove.send_packet_to_everyone("account_list", shove.accounts.get_entries_jsonable(key=lambda e: e["username"]))

            return f"Created account {username}"

        if command_args[0] == "delete":
            if len(command_args) == 1:  # /command delete
                if not user.is_logged_in():
                    raise UserNotLoggedIn

                delete_username = user.get_username()

            elif len(command_args) == 2:  # /command delete x
                delete_username = command_args_casing[1]

            else:
                raise CommandFailed(COMMANDS["account"]["usage"])

            try:
                found_account = shove.accounts.find_single(username=delete_username)
            except DatabaseEntryNotFound:
                raise CommandFailed(f"Account with username '{delete_username}' not found")

            for user in shove.get_all_users():
                if user.get_username() == delete_username:
                    shove.log_out_user(user)

            shove.accounts.remove_entry(found_account)
            shove.send_packet_to_everyone("account_list", shove.accounts.get_entries_jsonable(key=lambda e: e["username"]))

            return f"Deleted account {delete_username}"

        raise CommandFailed(COMMANDS["account"]["usage"])

    if is_command(command, "error"):  # raises an error to test error handling and logging
        raise Exception("/error was executed, all good")

    if is_command(command, "money"):
        if not user.is_logged_in():
            raise UserNotLoggedIn

        user.get_account()["money"] += 9e15
        shove.send_packet_to(user, "account_data", user.get_account_jsonable())
        return "Money added"

    if is_command(command, "trello"):
        if not PRIVATE_KEYS_IMPORTED:  # backend host has no access to private keys
            raise NoPrivateKeys

        trello_args = " ".join(command_args_casing).split(COMMANDS["trello"]["splitter"])
        if len(trello_args) == 1:
            name, description = trello_args[0], None

        elif len(trello_args) == 2:
            name, description = trello_args

        else:
            raise CommandFailed(f"Invalid arguments, usage: {COMMANDS['trello']['usage']}")

        if not name:
            raise CommandFailed(f"No card name, usage: {COMMANDS['trello']['usage']}")

        shove.add_trello_card(name, description)
        return "Card added"

    if is_command(command, "play"):
        if not PRIVATE_KEYS_IMPORTED:  # backend host has no access to private keys
            raise NoPrivateKeys

        if not command_args:
            raise CommandFailed(f"No link provided, usage: {COMMANDS['play']['usage']}")

        check_for_id_string = command_args_casing[0]

        # check if user dropped a plain YT id
        if len(check_for_id_string) == YOUTUBE_ID_LENGTH:
            youtube_id = check_for_id_string

        # regex magic to find the id in some url
        else:
            match = re.search(
                YOUTUBE_ID_REGEX_PATTERN,
                check_for_id_string
            )

            if not match:
                raise CommandFailed(f"Couldn't find a video ID in the given link, usage: {COMMANDS['play']['usage']}")

            youtube_id = match.group("id")
            Log.trace(f"Found ID using regex")

        Log.trace(f"Got YouTube ID: {youtube_id}")
        eventlet.spawn(process_song_task, shove, youtube_id, user)

        return "Success"

    raise CommandFailed(f"Unknown command: '{command}'")
