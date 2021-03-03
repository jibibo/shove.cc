from convenience import *


class Client:
    def __init__(self, sid: str):
        self.sid = sid
        self.account = None
        Log.trace(f"Created new Client for sid {sid}")

    def __repr__(self):
        return f"<Client {self.sid}, account: {self.account}>"

    def log_in(self):
        return

    def log_out(self):
        return
