from server_util import *
from server import Server


def handle_console_input(server, input_str):
    Log.trace(f"Handling console input '{input_str}'")

    if not input_str:
        raise StopServer

    input_split = input_str.split()
    input_len = len(input_split)

    if input_split[0] in ["stop", "quit", "exit"]:
        raise StopServer

    if input_split[0] in ["table"]:
        if input_len >= 2:
            table_name = " ".join(input_split[1:])
            found_table = server.get_table(table_name)
            if found_table:
                server.selected_table = found_table
                Log.info(f"Selected table {found_table}")
                return True
            else:
                Log.info(f"Table '{table_name}' not found")

        else:
            if server.selected_table:
                Log.info(f"Unselected table {server.selected_table}")
                server.selected_table = None
                return True
            else:
                Log.info(f"No table selected")

        return False

    if input_split[0] in ["tables"]:
        server.print_tables()
        return True

    if input_split[0] in ["player"]:
        Log.error("todo")
        return False

    if input_split[0] in ["players"]:
        players = []
        n_bots = 0

        for table in server.tables:
            for player in table.get_taken_seats_players().values():
                players.append(player)
                if player.is_bot:
                    n_bots += 1

        print(f"Players: {len(players)} (bots: {n_bots})")
        [print(player.data) for player in players]

        return True

    if input_split[0] in ["start"]:
        if server.selected_table:
            server.selected_table.try_to_start_game()
            return True

        else:
            Log.info(f"No table selected")
            return False


def listen_for_console_input(server):
    Log.info("Console input listener ready")
    while True:
        if server.selected_table:
            prompt = f"Table {server.selected_table}> "

        else:
            prompt = "Server> "

        input_str = input(prompt)

        try:
            success = handle_console_input(server, input_str)
            if not success:
                Log.info("Command failed")

        except StopServer:
            Log.trace("StopServer was caught")
            break

    Log.debug("Console input listener stopped")


def main():
    try:
        threading.current_thread().setName("Main")

        server = Server()

        listen_for_console_input(server)

    except Exception as ex:
        Log.fatal(f"UNHANDLED {type(ex).__name__} on main()", ex)

    Log.debug("Stopped main thread")


if __name__ == "__main__":
    # Log.trace("trace")
    # Log.debug("debug")
    # Log.info("info")
    # Log.warn("warn")
    # Log.error("error")
    # Log.fatal("fatal")
    main()
