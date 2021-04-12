from convenience import *

from accounts import Account


class User:
    """Someone who is connected to shove.cc, but not necessarily logged in"""

    def __init__(self, sid: str):
        self.sid = sid
        self._account: Union[Account, None] = None  # Union for editor type hints
        self._game_data: Union[dict, None] = None
        self.pinged_timestamp = 0
        self.last_pong_received = 0
        self.latency = 0
        Log.trace(f"Created new User object for SID '{sid}'")

    def __repr__(self):
        return f"<User name: {self.get_username()}, SID: {self.sid[:5]}>"

    def clear_game_data(self):
        """Clear any game data the user has"""
        self._game_data = None

    def get_account(self):
        return self._account

    def get_account_jsonable(self, filter_data=True) -> dict:
        if self._account:
            return self._account.get_jsonable(filter_data=filter_data)

    def get_game_data_copy(self, filter_keys=True) -> dict:  # todo should be DB entry-like
        if self._game_data:
            game_data = self._game_data.copy()
            if filter_keys:
                for key in []:
                    game_data[key] = "<filtered>"

            return game_data

    def get_username(self) -> str:
        """Returns None if user is not logged in"""

        if self.is_logged_in():
            return self._account["username"]

    def has_game_data(self) -> bool:
        if self._game_data:
            return True

        return False

    def is_logged_in(self) -> bool:
        if self._account:
            return True

        return False

    def log_in_as(self, account: Account):
        self._account = account
        Log.info(f"{self} logged in")
        return

    def log_out(self):
        self._account = None
        Log.info(f"{self} logged out")
        return

    def set_game_data(self, game_data: dict):
        self._game_data = game_data