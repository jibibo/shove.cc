from server_util import *


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
                self.handle_event(event)

            except DeleteTable:
                log(f"Deleting table '{self.name}'")  # todo implement
                break

        log("Stopped")

    def handle_event(self, event: str):
        log(f"Handling event...: {event}")

        if event == "player_added":
            self.table.try_to_start_game()
            return

        if event.startswith("game"):
            self.table.game.handle_event(event)
            return
