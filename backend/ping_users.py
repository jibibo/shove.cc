from convenience import *


class PingUsersThread(threading.Thread):
    def __init__(self, shove):
        super().__init__(name="PingUsersThread", daemon=True)
        self.shove = shove
        self.ping_interval = 5  # seconds, should be bigger than wait_before_disconnecting
        self.wait_before_disconnecting = 5  # when to disconnect a user after not receiving pong packet

    def run(self):
        Log.trace("Ready")
        elapsed = 0

        while True:
            if elapsed == self.wait_before_disconnecting:
                self.shove.disconnect_awaiting_pong_users()

            if elapsed == self.ping_interval:
                self.shove.ping_all_users()
                elapsed = 0

            time.sleep(1)
            elapsed += 1
