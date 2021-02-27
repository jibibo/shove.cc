from server_util import *


ACTION_BET = "BET"
ACTION_BLIND = "BLIND"
ACTION_CALL = "CALL"
ACTION_CHECK = "CHECK"
ACTION_FOLD = "FOLD"
ACTION_RAISE = "RAISE"


class Player:
    DEFAULT_DATA: dict = {  # always .copy() this
        "username": None,
        "password": None,

        "actions": 0,  # todo n_actions, as tracking player's actions over time is a future feature
        "all_in": False,
        "bet": 0,
        "cards": [],
        "chips": 100,
        "folded": False,
        "manual_bet_matches": False,  # forced big blind leaves this False
        "seat": 0,
    }

    def __init__(self, data: dict = None, bot_number=0):
        assert data or bot_number, "Player init with no data and not a bot"

        self.is_bot = bool(bot_number)

        if self.is_bot:
            self.bot_thread = None
            self.bot_aggressive_chance = 0  # round(random.uniform(0, 0.9), 2)
            self.bot_fold_chance = 0  # round(min(random.uniform(0, 0.5), 1 - self.bot_aggressive_chance), 2)
            Log.trace(f"Bot aggressive/fold chance: {self.bot_aggressive_chance}/{self.bot_fold_chance}")
            data = Player.DEFAULT_DATA.copy()
            data["username"] = f"Bot#{bot_number}"

        self.data = data

        Log.info(f"Created player {self}, is bot = {self.is_bot}")

    def __getitem__(self, key):
        try:
            return self.data[key]

        except KeyError as ex:
            Log.error(f"No such key in player data: {key}", ex)

    def __repr__(self):
        return f"<Player '{self['username']}', seat {self['seat']}, {self['chips']} chips>"

    def __setitem__(self, key, value):
        try:
            old = self.data[key]
            self.data[key] = value
            return old

        except KeyError as ex:
            Log.error(f"No such key in player data: {key}", ex)

    def __str__(self):
        return f"'{self['username']}'"

    def action(self, action, requested_chips=0) -> int:  # todo verify input, like calling with insufficient chips
        if action != ACTION_BLIND:
            self["actions"] += 1

        if action == ACTION_CHECK:
            Log.info(f"{self} checks")
            return 0

        if action == ACTION_FOLD:
            Log.info(f"{self} folds")
            self["folded"] = True
            return 0

        assert requested_chips, "requested chips to place not set, but given action does require this"

        if requested_chips > self["chips"]:
            placed_chips = self["chips"]
            Log.warn(f"Reduced requested amount that exceeded player's chip count ({requested_chips})")
        else:
            placed_chips = requested_chips

        old_chips = self["chips"]
        self["chips"] -= placed_chips
        self["bet"] += placed_chips

        Log.info(f"{self} placed {placed_chips} chip(s) ({action}), {self['chips']} left")

        if requested_chips >= old_chips:
            Log.info(f"{self} is all-in!")
            self["all_in"] = True

        if requested_chips <= old_chips and action != ACTION_BLIND:
            self["manual_bet_matches"] = True

        return placed_chips

    @staticmethod
    def create_from_username(username):  # todo get from existing db
        data = Player.DEFAULT_DATA.copy()
        data["username"] = username

        return Player(data)

    def generate_bot_decision(self, to_call, highest_bet, minimum_bet):
        Log.trace(f"{self} generating bot decision")

        if random.random() < self.bot_aggressive_chance:
            if highest_bet:
                return self.action(ACTION_RAISE, 2 * highest_bet)

            return self.action(ACTION_BET, minimum_bet)

        if to_call:
            if random.random() < self.bot_fold_chance:
                return self.action(ACTION_FOLD)

            return self.action(ACTION_CALL, to_call)

        return self.action(ACTION_CHECK)

    def new_hand_starting(self):
        self["chips"] = 100  # temp
        self["actions"] = 0
        self["cards"] = []
        self["manual_bet_matches"] = False
        self["all_in"] = False
        self["folded"] = False

    def post_blind(self, blind_amount):
        self.action(ACTION_BLIND, blind_amount)

    def won_chips(self, amount):
        self["chips"] += amount
        Log.info(f"{self} won {amount} chips, {self['chips']} total")