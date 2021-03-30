# packet handling errors

class PacketHandlingFailed(Exception):
    error = "unknown"
    description = "Unknown error (no description, not good)"


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
    error = "unknown"
    description = "No description provided"


class GameRunning(GameStartFailed):
    def __init__(self):
        self.description = "Game is already running"

    def __str__(self):
        return str(self.description)


class RoomEmpty(GameStartFailed):
    def __init__(self):
        self.description = "Room is empty"

    def __str__(self):
        return str(self.description)


# other exceptions

class GameEventInvalid(Exception):
    def __init__(self, description):
        self.description = description or "Game event failed"

    def __str__(self):
        return str(self.description)


class GameEventNotImplemented(Exception):
    pass

