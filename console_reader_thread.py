from util import *


# todo input() massively slows down flask startup? implement chrome admin console instead
class ConsoleReaderThread(threading.Thread):
    def __init__(self, server):
        super().__init__(name="ConsoleReader", daemon=True)
        self.server = server

    def run(self):
        Log.trace("Running")

        while True:
            if self.server.selected_table:
                prompt = f"Table {self.server.selected_table}"

            else:
                prompt = "Server"

            input_str = input(f"{prompt}> ")

            try:
                success = self.handle_console_input(input_str)
                if not success:
                    Log.info("Command failed")

            except BaseException as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on handling console input", exception=ex)
                continue

    def handle_console_input(self, input_str):
        Log.trace(f"Handling console input '{input_str}'")

        if not input_str:
            return  # sys.exit()

        input_split = input_str.split()
        input_len = len(input_split)

        if input_split[0] in ["stop", "quit", "exit"]:
            return  # sys.exit()

        if input_split[0] in ["table"]:
            if input_len >= 2:
                table_name = " ".join(input_split[1:])
                found_table = self.server.get_table(table_name)
                if found_table:
                    self.server.selected_table = found_table
                    Log.info(f"Selected table {found_table}")
                    return True
                else:
                    Log.info(f"Table '{table_name}' not found")

            else:
                if self.server.selected_table:
                    Log.info(f"Unselected table {self.server.selected_table}")
                    self.server.selected_table = None
                    return True
                else:
                    Log.info(f"No table selected")

            return False

        if input_split[0] in ["tables"]:
            self.server.print_tables()
            return True

        if input_split[0] in ["player"]:
            Log.error("todo")
            return False

        if input_split[0] in ["participating_players"]:
            players = []
            n_bots = 0

            for table in self.server.tables:
                for player in table.get_taken_seats_players().values():
                    players.append(player)
                    if player.is_bot:
                        n_bots += 1

            print(f"Players: {len(players)} (bots: {n_bots})")
            [print(player.data) for player in players]

            return True

        if input_split[0] in ["start"]:
            if self.server.selected_table:
                self.server.selected_table.try_to_start_game()
                return True

            else:
                Log.info(f"No table selected")
                return False
