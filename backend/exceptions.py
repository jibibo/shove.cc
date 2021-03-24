# packet handling errors

class PacketHandlingError(Exception):
    error = "error_missing"
    description = "description_missing"


class AccountNotFound(PacketHandlingError):
    error = "account_not_found"
    description = "Account not found"


class CommandInvalid(PacketHandlingError):
    error = "command_invalid"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class GameActionFailed(PacketHandlingError):
    error = "game_action_failed"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class GameNotSet(PacketHandlingError):
    error = "game_not_set"
    description = "Room has no game set"


class PacketInvalid(PacketHandlingError):
    error = "packet_invalid"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class PacketNotImplemented(PacketHandlingError):
    error = "packet_not_implemented"
    description = "Packet not implemented (yet)"


class PasswordInvalid(PacketHandlingError):
    error = "password_invalid"
    description = "Invalid password"


class RoomFull(PacketHandlingError):
    error = "room_full"
    description = "Room is full"


class RoomNotFound(PacketHandlingError):
    error = "room_not_found"
    description = "Room not found"


class UserUnauthorized(PacketHandlingError):
    error = "user_unauthorized"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class UserAlreadyInRoom(PacketHandlingError):
    error = "user_already_in_room"
    description = "Already in a room"


class UserNotInRoom(PacketHandlingError):
    error = "user_not_in_room"
    description = "Not in a room"


# game start errors

class GameStartError(Exception):
    error = "error_missing"
    description = "description_missing"


class GameRunning(GameStartError):
    def __init__(self):
        self.description = "Game is already running"

    def __str__(self):
        return str(self.description)


class RoomEmpty(GameStartError):
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

