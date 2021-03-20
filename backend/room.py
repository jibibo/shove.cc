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

        # todo each game should have their own event handler (if needed)

        Log.info(f"Created room {self}")

    def __repr__(self):
        return f"<Room '{self.name}', {self.get_user_count()} users>"

    def __str__(self):
        return f"'{self.name}'"

    def get_user_count(self) -> int:
        return len(self._users)

    def get_users(self) -> List[User]:
        return self._users.copy()

    def is_empty(self):
        return self.get_user_count() == 0

    def send_packet(self, model: str, packet: dict, skip: Union[User, List[User]] = None):
        self.shove.send_packet(self.get_users(), model, packet, skip)

    def try_to_start_game(self):
        Log.trace("Trying to start game")

        try:
            fail_reason = self.game.try_to_start()

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on self.game.try_to_start", ex)
            return

        if fail_reason:
            Log.info(f"Could not start game in room {self}, reason: {fail_reason}")

        else:
            Log.info(f"Game started in room {self}")

    def user_tries_to_join(self, user: User) -> Union[None, str]:
        """Returns a reason if could not join room (if rejected by the room's game), otherwise None"""

        Log.trace("Trying to let user join room")

        if self.game:
            fail_reason = self.game.user_tries_to_join_room(user)

            if fail_reason:
                return fail_reason

        self._users.append(user)  # if game is not set, user can always join

    def user_leave(self, user: User):
        self.game.user_left_room(user)
        self._users.remove(user)
