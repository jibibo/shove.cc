from util_server import *
from server import Server


def handle_console_input(server, input_str):
    if not input_str:
        raise StopServer

    input_split = input_str.split()
    if input_split[0] in ["stop", "quit", "exit"]:
        raise StopServer

    if input_split[0] in ["tables", "t"]:
        server.print_tables()
        return True


def main():
    threading.current_thread().setName("Main")
    log("Starting server", LogLevel.INFO)
    server = Server()

    log("Console input ready", LogLevel.INFO)
    while True:
        input_str = input()

        try:
            success = handle_console_input(server, input_str)
            if not success:
                log("Command unsuccessful", LogLevel.INFO)

        except StopServer:
            break

    log("Stopped server", LogLevel.INFO)


if __name__ == "__main__":
    main()
