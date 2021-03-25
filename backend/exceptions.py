# packet handling errors

class PacketHandlingFailed(Exception):
    error = "unknown"
    description = "No description provided"


class AccountNotFound(PacketHandlingFailed):
    error = "account_not_found"
    description = "Account not found"


class CommandInvalid(PacketHandlingFailed):
    error = "command_invalid"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class GameActionFailed(PacketHandlingFailed):
    error = "game_action_failed"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class GameNotSet(PacketHandlingFailed):
    error = "game_not_set"
    description = "Room has no game set"


class PacketInvalid(PacketHandlingFailed):
    error = "packet_invalid"

    def __init__(self, description=None):
        self.description = description or "No description provided"

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
    description = "Not logged in"


class UserUnauthorized(PacketHandlingFailed):
    error = "user_unauthorized"

    def __init__(self, description=None):
        self.description = description or "No description provided"

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
        self.description = description

    def __str__(self):
        return str(self.description)


class GameEventNotImplemented(Exception):
    pass

