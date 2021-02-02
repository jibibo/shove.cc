from util_client import *
from client import Client


def handle_console_input(client, input_str):
    if not input_str:
        raise Exit

    input_split = input_str.split()
    if input_split[0] in ["quit", "exit"]:
        raise Exit


def main():
    threading.current_thread().setName("Main")
    log("Starting client", LogLevel.INFO)
    client = Client()

    log("Console input ready", LogLevel.INFO)
    while True:
        input_str = input()

        try:
            success = handle_console_input(client, input_str)
            if not success:
                log("Command unsuccessful", LogLevel.INFO)

        except Exit:
            break

    log("Exiting", LogLevel.INFO)


if __name__ == "__main__":
    main()
