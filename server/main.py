from server_util import *
from server import Server


def handle_console_input(server, input_str):
    log(f"Handling console input... '{input_str}'", LOG_DEBUG)

    if not input_str:
        raise StopServer

    input_split = input_str.split()
    if input_split[0] in ["stop", "quit", "exit", "q"]:
        raise StopServer

    if input_split[0] in ["tables", "t"]:
        server.print_tables()
        return True

    if input_split[0] in ["players", "p"]:
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

    if input_split[0] in ["start", "s"]:
        server.tables[0].try_to_start_game()
        return True


def listen_for_console_input(server):
    log("Console input listener ready", LOG_INFO)
    while True:
        input_str = input()

        try:
            success = handle_console_input(server, input_str)
            if not success:
                log("Command failed", LOG_INFO)

        except StopServer:
            log("StopServer was caught")
            break

    log("Console input listener stopped", LOG_INFO)


def main():
    try:
        threading.current_thread().setName("Main")

        server = Server()

        listen_for_console_input(server)

    except Exception as ex:
        log(f"UNHANDLED {type(ex).__name__} on main()", LOG_ERROR, ex)

    log("Stopped main thread", LOG_INFO)


if __name__ == "__main__":
    main()
