DEFAULT_DESCRIPTION = "Unknown error (no description, not good)"


# packet handling errors

class PacketHandlingFailed(Exception):
    description = DEFAULT_DESCRIPTION


class AccountNotFound(PacketHandlingFailed):
    description = "Account not found"


class GameActionFailed(PacketHandlingFailed):
    def __init__(self, description=None):
        self.description = description or "Game action failed"

    def __str__(self):
        return str(self.description)


class GameNotSet(PacketHandlingFailed):
    description = "Room has no game set"


class NoPrivateAccess(PacketHandlingFailed):
    description = "Backend host has no access to private information (not good)"


class PacketInvalid(PacketHandlingFailed):
    def __init__(self, description=None):
        self.description = description or "Invalid packet"

    def __str__(self):
        return str(self.description)


class PacketNotImplemented(PacketHandlingFailed):
    description = "Packet not implemented (yet)"


class PasswordInvalid(PacketHandlingFailed):
    description = "Invalid password"


class RoomFull(PacketHandlingFailed):
    description = "Room is full"


class RoomNotFound(PacketHandlingFailed):
    description = "Room not found"


class UserAlreadyInRoom(PacketHandlingFailed):
    description = "Already in a room"


class UserNotInRoom(PacketHandlingFailed):
    description = "Not in a room"


class UserNotLoggedIn(PacketHandlingFailed):
    def __init__(self, description=None):
        self.description = description or "User not logged in"

    def __str__(self):
        return str(self.description)


class UserUnauthorized(PacketHandlingFailed):
    def __init__(self, description=None):
        self.description = description or "User unauthorized"

    def __str__(self):
        return str(self.description)


# game start errors

class GameStartFailed(Exception):
    description = DEFAULT_DESCRIPTION


class GameRunning(GameStartFailed):
    description = "Game is already running"


class RoomEmpty(GameStartFailed):
    description = "Room is empty"


# other exceptions

class CommandInvalid(Exception):
    def __init__(self, description=None):
        self.description = description or "Invalid command"

    def __str__(self):
        return str(self.description)


class GameEventInvalid(Exception):
    def __init__(self, description):
        self.description = description or "Game event failed"

    def __str__(self):
        return str(self.description)


class GameEventNotImplemented(Exception):
    pass


class ConvertAudioFailed(Exception):
    def __init__(self, description):
        self.description = str(description)

    def __str__(self):
        return self.description


class DownloadAudioFailed(Exception):
    def __init__(self, description):
        self.description = str(description)

    def __str__(self):
        return self.description
