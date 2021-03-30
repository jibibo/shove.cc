_DEFAULT_ERROR = "unknown"
_DEFAULT_DESCRIPTION = "Unknown error (no description, not good)"


# packet handling errors

class PacketHandlingFailed(Exception):
    error = _DEFAULT_ERROR
    description = _DEFAULT_DESCRIPTION


class AccountNotFound(PacketHandlingFailed):
    error = "account_not_found"
    description = "Account not found"


class CommandInvalid(PacketHandlingFailed):
    error = "command_invalid"

    def __init__(self, description=None):
        self.description = description or "Invalid command"

    def __str__(self):
        return str(self.description)


class GameActionFailed(PacketHandlingFailed):
    error = "game_action_failed"

    def __init__(self, description=None):
        self.description = description or "Game action failed"

    def __str__(self):
        return str(self.description)


class GameNotSet(PacketHandlingFailed):
    error = "game_not_set"
    description = "Room has no game set"


class NoPrivateAccess(PacketHandlingFailed):
    error = "no_private_access"
    description = "Backend host has no access to private information (not good)"


class PacketInvalid(PacketHandlingFailed):
    error = "packet_invalid"

    def __init__(self, description=None):
        self.description = description or "Invalid packet"

    def __str__(self):
        return str(self.description)


class PacketNotImplemented(PacketHandlingFailed):
    error = "packet_not_implemented"
    description = "Packet not implemented (yet)"


class PasswordInvalid(PacketHandlingFailed):
    error = "password_invalid"
    description = "Invalid password"


class RoomFull(PacketHandlingFailed):
    error = "room_full"
    description = "Room is full"


class RoomNotFound(PacketHandlingFailed):
    error = "room_not_found"
    description = "Room not found"


class UserAlreadyInRoom(PacketHandlingFailed):
    error = "user_already_in_room"
    description = "Already in a room"


class UserNotInRoom(PacketHandlingFailed):
    error = "user_not_in_room"
    description = "Not in a room"


class UserNotLoggedIn(PacketHandlingFailed):
    error = "user_not_logged_in"

    def __init__(self, description=None):
        self.description = description or "User not logged in"

    def __str__(self):
        return str(self.description)


class UserUnauthorized(PacketHandlingFailed):
    error = "user_unauthorized"

    def __init__(self, description=None):
        self.description = description or "User unauthorized"

    def __str__(self):
        return str(self.description)


# game start errors

class GameStartFailed(Exception):
    error = _DEFAULT_ERROR
    description = _DEFAULT_DESCRIPTION


class GameRunning(GameStartFailed):
    error = "game_running"
    description = "Game is already running"


class RoomEmpty(GameStartFailed):
    error = "room_empty"
    description = "Room is empty"


# other exceptions

class GameEventInvalid(Exception):
    def __init__(self, description):
        self.description = description or "Game event failed"

    def __str__(self):
        return str(self.description)


class GameEventNotImplemented(Exception):
    pass

