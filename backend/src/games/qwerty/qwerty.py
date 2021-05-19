from convenience import *

from abstract_game import AbstractGame
from user import User


class Qwerty(AbstractGame):
    def __init__(self, room):
        super().__init__(room)
        self.words = []
        with open("src/games/qwerty/english.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                self.words.append(line[:-2])  # dont include the trailing \n

    def get_data(self, event: str = None) -> dict:
        return {
            "name": self.get_name(),  # unused
            "state": self.state,
            "player_data": {user.get_username(): user.get_game_data_copy()
                            for user in self.players},
        }

    def get_random_words(self, n=10):
        return random.choices(self.words, k=n)

    def handle_event(self, event: str):
        if event == "user_joined":
            return

        raise GameEventInvalid

    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        if packet["kind"] == "submit_word":

            return

        raise PacketHandlingFailed

    def try_to_start(self):
        pass

    def user_leaves_room(self, user: User, skip_event=False):
        self.events.put("user_left")

    def user_tries_to_join_room(self, user: User):
        self.players.append(user)
        user.set_game_data({
            "words": self.get_random_words()
        })
        self.broadcast_data()
        self.events.put("user_joined")