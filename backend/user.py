from convenience import *
from account import Account


class User:
    def __init__(self, sid: str):
        self.sid = sid
        self._account = None
        self.game_data: dict = {}
        self.ping_timestamp = 0
        Log.trace(f"Created new User object for SID {sid}")

    def __repr__(self):
        return f"<User {self}, account: {self._account}>"

    def __str__(self):
        if self._account:
            return f"'{self._account['username']}/{self.sid}'"

        else:
            return f"'{self.sid}'"

    def clear_game_data(self):
        self.game_data.clear()

    def get_account(self) -> Account:
        if self._account:
            return self._account

    def get_account_data(self, filter_sensitive=True) -> dict:
        if self._account:
            account_data = self._account.get_data().copy()

            if filter_sensitive:
                for key in ["password"]:
                    account_data[key] = "<filtered>"

            return account_data

    def get_game_data(self, filter_sensitive=True) -> dict:
        if self.game_data:
            game_data = self.game_data.copy()
            if filter_sensitive:
                for key in []:
                    game_data[key] = "<filtered>"

            return game_data

    def get_username(self) -> str:
        """Returns None if user is not logged in"""

        if self._account:
            return self._account["username"]

    def is_logged_in(self) -> bool:
        if self._account:
            return True

        return False

    def log_in(self, account: Account):
        self._account = account
        Log.info(f"{self} logged in")
        return

    def log_out(self):
        self._account = None
        Log.info(f"{self} logged out")
        return
