from convenience import *
from account import Account


class User:
    def __init__(self, sid: str):
        self.sid = sid
        self._account = None
        self.game_data: dict = {}
        Log.trace(f"Created new User object for SID {sid}")

    def __repr__(self):
        return f"<User {self}, account: {self._account}>"

    def __str__(self):
        if self._account:
            return f"'{self._account['username']}/{self.sid}'"

        else:
            return f"'{self.sid}'"

    def clear_game_data(self):
        self.game_data = {}

    def get_account(self) -> Account:
        if self._account:
            return self._account

    def get_username(self) -> str:
        """Returns None if user is not logged in"""

        if self._account:
            return self._account["username"]

        Log.warn(f"Could not get username of {self}: account not set")

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
