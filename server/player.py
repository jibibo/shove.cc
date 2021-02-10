from util_server import *


class Player:
    DEFAULT_DATA: dict = {
        "username": None,
        "password": None,
        "chips": 100,
        "bet": 0,
        "cards": []
    }

    def __init__(self, data: dict=None, is_bot=False):
        assert data or is_bot, "Player init with no data and not a bot"

        self.is_bot = is_bot

        if is_bot:
            data = Player.DEFAULT_DATA
            data["username"] = "Bot"

        self.data = data

        log(f"Created player {self}")

    def __getitem__(self, item):
        assert item in self.data.keys(), "no such key in player data"

        return self.data[item]

    def __repr__(self):
        return f"'{self['username']}'"

    def __setitem__(self, key, value):
        assert key in self.data.keys(), "no such key in player data"

        old = self.data[key]
        self.data[key] = value

        return old

    @classmethod
    def create_bot(cls):
        return cls(is_bot=True)

    @classmethod
    def create_from_username(cls, username):
        data = Player.DEFAULT_DATA
        data["username"] = username

        return cls(data)