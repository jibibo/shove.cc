class PacketHandlingError(Exception):
    error = "error_missing"
    description = "description_missing"


# children of PacketHandling Error

class AccountNotFound(PacketHandlingError):
    error = "account_not_found"
    description = "Account not found"


class GameActionFailed(PacketHandlingError):
    error = "game_action_failed"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class GameNotSet(PacketHandlingError):
    error = "game_not_set"
    description = "Room has no game set"


class PacketCommandInvalid(PacketHandlingError):
    error = "command_invalid"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class PacketInvalid(PacketHandlingError):
    error = "packet_invalid"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class PacketNotImplemented(PacketHandlingError):
    error = "packet_not_implemented"
    description = "Packet not implemented (yet)"


class PacketUserUnauthorized(PacketHandlingError):
    error = "user_unauthorized"

    def __init__(self, description=None):
        self.description = description or "No description provided"

    def __str__(self):
        return str(self.description)


class RoomFull(PacketHandlingError):
    error = "room_full"
    description = "Room is full"


class RoomNotFound(PacketHandlingError):
    error = "room_not_found"
    description = "Room not found"


# exceptions that are not (yet) children of PacketHandlingError

class GameEventInvalid(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)


class GameEventNotImplemented(Exception):
    pass


class GameRunning(Exception):
    pass


class RoomEmpty(Exception):
    pass

