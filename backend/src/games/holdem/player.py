from src.convenience import *


ACTION_BET = "BET"
ACTION_BLIND = "BLIND"
ACTION_CALL = "CALL"
ACTION_CHECK = "CHECK"
ACTION_FOLD = "FOLD"
ACTION_RAISE = "RAISE"


class Player:  # todo this is a Holdem player, so move it to holdem game package
    DEFAULT_DATA: dict = {  # always .copy() this
        "username": None,
        "password": None,
        "seat": 0,

        "all_in": False,
        "bet": 0,
        "cards": [],
        "chips": 100,
        "folded": False,
        "had_action": False,  # forced big blind leaves this False
    }

    def __init__(self, data: dict = None, bot_number=0):
        assert data or bot_number, "Player init with no data and not a bot"

        self.is_bot = bool(bot_number)

        if self.is_bot:
            self.bot_thread = None
            self.bot_aggressive_chance = round(random.uniform(0, 0.9), 2)
            self.bot_fold_chance = round(min(random.uniform(0, 0.5), 1 - self.bot_aggressive_chance), 2)
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
        return f"<Player '{self['username']}', seat {self['seat']}, stack: {self['chips']} chips>"

    def __setitem__(self, key, value):
        try:
            old = self.data[key]
            self.data[key] = value
            return old

        except KeyError as ex:
            Log.error(f"No such key in player data: {key}", ex)

    def __str__(self):
        return f"'{self['username']}'"

    def action(self, action, requested_place_chips=0) -> int:  # todo verify input, like calling with insufficient chips
        if action != ACTION_BLIND:
            self["had_action"] = True

        if action == ACTION_CHECK:
            Log.info(f"{self} checks")
            return 0

        if action == ACTION_FOLD:
            Log.info(f"{self} folds")
            self["folded"] = True
            return 0

        assert requested_place_chips, "requested chips to place not set, but given action does require this"

        if requested_place_chips > self["chips"]:
            place_chips = self["chips"]
            Log.warn(f"Reduced requested amount that exceeded player's chip count ({requested_place_chips} -> {place_chips})")
        else:
            place_chips = requested_place_chips

        self.place_chips(place_chips, action)
        return place_chips

    @staticmethod
    def create_from_username(username):  # todo get from existing db
        data = Player.DEFAULT_DATA.copy()
        data["username"] = username

        return Player(data)

    def decide_bot_action(self, game):
        last_bet = game.last_bet
        minimum_bet = 2 * game.blind_amount
        to_call = last_bet - self["bet"]
        Log.trace(f"{self} deciding bot action, bet: {self['bet']}, to call: {to_call}, last bet: {last_bet}, min bet: {minimum_bet}")

        if random.random() < self.bot_aggressive_chance:
            if last_bet:
                return self.action(ACTION_RAISE, 2 * last_bet)

            return self.action(ACTION_BET, minimum_bet)

        if to_call:
            if random.random() < self.bot_fold_chance:
                return self.action(ACTION_FOLD)

            return self.action(ACTION_CALL, to_call)

        return self.action(ACTION_CHECK)

    def new_hand_started(self):
        self["bet"] = 0
        # self["chips"] = 100  # reset chips on each hand
        self["cards"] = []
        self["had_action"] = False
        self["all_in"] = False
        self["folded"] = False

    def next_street_started(self):
        self["bet"] = 0
        self["had_action"] = False

    def place_chips(self, place_chips, action):
        assert place_chips <= self["chips"], "requested too many chips"

        self["chips"] -= place_chips
        self["bet"] += place_chips
        self.update_all_in_status()

        Log.info(f"{self} placed {place_chips} chip(s) ({action}), bet: {self['bet']}, stack: {self['chips']}")

    def post_blind(self, blind_amount):
        self.action(ACTION_BLIND, blind_amount)

    def return_excess_chips(self, excess_chips):
        assert excess_chips > 0, "no excess chips amount given"

        self["chips"] += excess_chips
        self["bet"] -= excess_chips
        self.update_all_in_status()
        Log.trace(f"Returned {excess_chips} excess bet chips to {self}")

    def update_all_in_status(self):
        if self["chips"] == 0:
            self["all_in"] = True
            Log.info(f"{self} is all-in")
        elif self["all_in"]:
            self["all_in"] = False
            Log.info(f"{self} is no longer all-in")

    def won_chips(self, amount, name, rank, percentile):
        self["chips"] += amount
        Log.info(f"{self} won {amount} chips with a {name} (top {round(percentile * 100, 2)}%, rank {rank})")
