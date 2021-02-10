from util_server import *


class DeleteTable(BaseException):
    pass


class TableHandler(threading.Thread):
    def __init__(self, table):
        self.table = table
        super().__init__(name=f"TableHandler/{table.name}", daemon=True)

    def run(self):
        log("Ready")

        while True:
            event = self.table.events.get()

            try:
                self.handle(event)

            except DeleteTable:
                log(f"Deleting table '{self.name}'")  # todo implement
                break

        log("Thread exiting run()")

    def handle(self, event):
        log(f"Handling event...: {event}")

        if event == "player_added":
            if self.table.state != STATE_WAITING:
                return

            self.table.attempt_start()
            return

        if event == "started":
            self.table.send_players({"model": "started"})
            return