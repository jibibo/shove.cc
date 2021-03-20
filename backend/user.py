from convenience import *
from account import Account


class User:
    def __init__(self, sid: str):
        self.sid = sid
        self.account = None
        Log.trace(f"Created new User object for SID {sid}")

    def __repr__(self):
        return f"<User {self}, account: {self.account}>"

    def __str__(self):
        if self.account:
            return f"'{self.account['username']}/{self.sid}'"

        else:
            return f"'{self.sid}'"

    def log_in(self, account: Account):
        self.account = account
        Log.info(f"{self} logged in")
        return

    def log_out(self):
        self.account = {}
        Log.info(f"{self} logged out")
        return
