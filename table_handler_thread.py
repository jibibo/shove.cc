from util import *


class DeleteTable(Exception):
    pass


class TableHandlerThread(threading.Thread):
    def __init__(self, table):
        self.table = table
        super().__init__(name=f"TableHandler/{table.name}", daemon=True)

    def run(self):
        Log.debug("Ready")

        while True:
            event = self.table.events.get()

            try:
                self.handle_event(event)

            except DeleteTable:
                Log.trace(f"Deleting table '{self.name}'")  # todo implement
                break

        Log.debug("Stopped")

    def handle_event(self, event: str):
        Log.trace(f"Handling event: {event}")

        if event in ["player_added"]:
            return

        if event in ["start"]:
            self.table.try_to_start_game()
            return

        if event.startswith("game"):
            self.table.game.handle_event(event)
            return
