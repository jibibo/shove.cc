from server_util import *


class Player:
    DEFAULT_DATA: dict = {  # always .copy() this
        "username": None,
        "password": None,

        "active": False,
        "all_in": False,
        "bet": 0,
        "blind_placement_skip_bet": False,
        "cards": [],
        "chips": 100,
        "folded": False,
        "seat": 0,
    }

    def __init__(self, data: dict=None, is_bot=False):
        assert data or is_bot, "Player init with no data and not a bot"

        self.is_bot = is_bot

        if is_bot:
            self.bot_thread = None
            data = Player.DEFAULT_DATA.copy()
            data["username"] = f"Bot{random.randint(0, 9999)}"

        self.data = data

        log(f"Created player {self}, bot = {self.is_bot}")

    def __getitem__(self, key):
        try:
            return self.data[key]

        except KeyError as ex:
            log(f"No such key in player data: {key}", LOG_ERROR, ex)

    def __repr__(self):
        return f"<Player '{self['username']}', {self['chips']} chips, seat {self['seat']}>"

    def __setitem__(self, key, value):
        assert key in self.data.keys(), "no such key in player data"

        old = self.data[key]
        self.data[key] = value

        return old

    def __str__(self):
        return f"'{self['username']}'"

    def bet(self, amount) -> int:
        real_amount = min(amount, self["chips"])
        assert real_amount > 0, "no chips left, failed to check"

        self["chips"] -= real_amount  # todo check for all in etc
        self["bet"] += real_amount

        log(f"{self} bet {real_amount}, {self['chips']} chips left", LOG_INFO)

        return real_amount

    def bot_action(self, table):
        log(f"Processing bot action for {self}")
        highest_bet_this_street = table.highest_bet_this_street
        to_call = highest_bet_this_street - self["bet"]
        if to_call:
            self.bet(to_call)
        else:
            self.check()

    def check(self):
        log(f"{self} checked", LOG_INFO)

    @staticmethod
    def create_from_username(username):  # todo get from existing db
        data = Player.DEFAULT_DATA.copy()
        data["username"] = username

        return Player(data)

    # def fold(self):
    #     pass

    def won_chips(self, amount):
        self["chips"] += amount
        log(f"{self} won {amount} chips, total: {self['chips']}")