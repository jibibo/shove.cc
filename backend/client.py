from convenience import *


class Client:
    def __init__(self, sid: str):
        self.sid = sid
        self.account_data = None
        Log.trace(f"Created new Client for sid {sid}")

    def __repr__(self):
        return f"<Client {self.sid}, account: {self.account_data}>"

    def log_in(self, account_data):
        self.account_data = account_data
        Log.trace(f"{self} logged in")
        return

    def log_out(self):
        self.account_data = None
        Log.trace(f"{self} logged out")
        return
