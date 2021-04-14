from convenience import *
from abstract_game import AbstractGame
from user import User


class Room:
    def __init__(self, shove):
        self.shove = shove
        self.id = shove.get_next_room_id()
        self.name = f"Room#{self.id}"
        self._users: Set[User] = set()
        self.max_user_count: int = 0

        self.game: AbstractGame = shove.get_default_game()(self)

        Log.info(f"Created room {self}")

    def __repr__(self):
        return f"<Room #{self.id}, name: '{self.name}', {self.get_user_count()} users>"

    def get_data(self) -> dict:
        return {
            "name": self.name,
            "user_count": self.get_user_count(),
            "max_user_count": self.max_user_count
        }

    def get_user_count(self) -> int:
        return len(self._users)

    def get_users(self) -> Set[User]:
        return self._users

    def is_empty(self):
        return self.get_user_count() == 0

    def is_full(self):
        return self.max_user_count and self.get_user_count() >= self.max_user_count

    def send_packet_to_occupants(self, model: str, packet: Union[dict, list], skip: Union[User, Set[User]] = None):
        """Send packet to everyone in this room"""

        self.shove.send_packet_to(self.get_users(), model, packet, skip)

    def try_to_start_game(self):
        Log.trace(f"Trying to start game in room {self}")

        try:
            self.game.try_to_start()

        except GameStartFailed as ex:
            Log.trace(f"Game start failed: {ex.description}")

        except Exception as ex:
            Log.critical("Unhandled exception on try_to_start", ex=ex)

        else:
            Log.info(f"Game started in room {self}")

    def user_tries_to_join(self, user: User):
        """Tries to put user in the room, if fails, throws an exception"""

        Log.trace(f"Trying to let user {user} join room {self}")

        if not user.is_logged_in():
            raise UserNotLoggedIn("Log in to join this room")

        if self.is_full():
            raise RoomFull

        if self.game:  # if game is not set, user can join for sure
            self.game.user_tries_to_join_room(user)

        self._users.add(user)

        # update room list for all connected users
        self.shove.send_packet_to_everyone("room_list", [room.get_data() for room in self.shove.get_rooms()])

        Log.info(f"{user} joined room {self}")

    def user_leave(self, user: User, skip_list_packet=False, skip_game_event=False):
        """Method for the room to handle when a user leaves the room.
        Clears user's game data as well."""

        Log.trace(f"Removing user {user} from room {self}")

        if self.game:
            try:
                self.game.user_leaves_room(user, skip_event=skip_game_event)

            except Exception as ex:
                Log.critical("Unhandled exception on user_left_room", ex=ex)

            user.clear_game_data()

        self._users.remove(user)

        if not skip_list_packet:
            # update room list for all connected users
            self.shove.send_packet_to_everyone("room_list", [room.get_data() for room in self.shove.get_rooms()])

        Log.trace(f"Removed user {user} from room {self}")
