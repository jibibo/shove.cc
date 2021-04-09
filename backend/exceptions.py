DEFAULT_DESCRIPTION = "Unknown error (no description, not good)"


# packet handling errors

class PacketHandlingFailed(Exception):
    description = DEFAULT_DESCRIPTION


class DatabaseEntryNotFound(PacketHandlingFailed):
    description = "Database entry not found"


class GameActionFailed(PacketHandlingFailed):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)


class GameNotSet(PacketHandlingFailed):
    description = "Room has no game set"


class NoPrivateAccess(PacketHandlingFailed):
    description = "Backend host has no access to private information (not good)"


class NoSongsAvailable(PacketHandlingFailed):
    description = "No songs available"


class PacketMissing(PacketHandlingFailed):
    description = "Model is missing a (required) packet"


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
    description = "User not logged in"


class UserUnauthorized(PacketHandlingFailed):
    description = "User unauthorized"


# game start errors

class GameStartFailed(Exception):
    description = DEFAULT_DESCRIPTION


class GameRunning(GameStartFailed):
    description = "Game is already running"


class RoomEmpty(GameStartFailed):
    description = "Room is empty"


# song processing


class SubprocessFailed(Exception):
    def __init__(self, description):
        self.description = str(description)

    def __str__(self):
        return self.description


class ExtractSongInformationFailed(Exception):
    def __init__(self, description):
        self.description = str(description)

    def __str__(self):
        return self.description


# other exceptions

class CommandFailed(Exception):
    def __init__(self, description="Command failed"):
        self.description = description

    def __str__(self):
        return str(self.description)


class GameEventInvalid(Exception):
    def __init__(self, description="Game event invalid"):
        self.description = description

    def __str__(self):
        return str(self.description)
