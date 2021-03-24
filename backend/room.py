from convenience import *
from base_game import BaseGame
from user import User


class Room:
    MIN_PLAYERS = 2

    def __init__(self, shove):
        self.shove = shove
        self.name = f"R{shove.get_room_count() + 1}"
        self.game: BaseGame = shove.get_default_game()(self)
        self._users: List[User] = []
        self.max_user_count: int = 0

        Log.info(f"Created room {self}")

    def __repr__(self):
        return f"<Room '{self.name}', {self.get_user_count()} users>"

    def __str__(self):
        return f"'{self.name}'"

    def get_data(self) -> dict:
        return {
            "name": self.name,
            "user_count": self.get_user_count(),
            "max_user_count": self.max_user_count
        }

    def get_user_count(self) -> int:
        return len(self._users)

    def get_users(self) -> List[User]:
        return self._users.copy()

    def is_empty(self):
        return self.get_user_count() == 0

    def is_full(self):
        return self.max_user_count and self.get_user_count() >= self.max_user_count

    def send_packet_all(self, model: str, packet: dict, skip: Union[User, List[User]] = None):
        self.shove.send_packet(self.get_users(), model, packet, skip)

    def try_to_start_game(self):
        Log.trace(f"Trying to start game in room {self}")

        try:
            self.game.try_to_start()

        except GameStartError as ex:
            Log.trace(f"Could not start game: {ex}")

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on room.game.try_to_start", ex)

        else:
            Log.info(f"Game started in room {self}")

    def user_tries_to_join(self, user: User):
        """Tries to put user in the room, if fails, throws an exception"""

        Log.trace(f"Trying to let user {user} join room {self}")

        if self.is_full():
            raise RoomFull

        if self.game:  # if game is not set, user can join for sure
            self.game.user_tries_to_join_room(user)  # tries to drop user in the room, if fails, raises exception

        self._users.append(user)

        self.shove.send_packet_all("room_list", {  # update room list for all connected users
            "room_list": [room.get_data() for room in self.shove.get_rooms()]
        })

        Log.info(f"{user} joined room {self}")

    def user_leave(self, user: User):
        Log.trace(f"User {user} is leaving room {self}")

        if self.game:
            try:
                self.game.user_left_room(user)

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on room.game.user_left_room", ex)

            user.clear_game_data()  # clear any game data the user could have because of the game they left

        self._users.remove(user)

        self.shove.send_packet_all("room_list", {  # update room list for all connected users
            "room_list": [room.get_data() for room in self.shove.get_rooms()]
        })

        Log.trace(f"User {user} left room {self}")
