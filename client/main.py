from util_client import *
from client import Client


def handle_console_input(client, input_str):
    log(f"Handling console input: '{input_str}'", LOG_DEBUG)

    if not input_str:
        raise Exit

    input_split = input_str.split()
    if input_split[0] in ["quit", "exit"]:
        raise Exit


def main():
    threading.current_thread().setName("Main")
    client = Client()

    log("Console input ready", LOG_INFO)
    while True:
        input_str = input()

        try:
            success = handle_console_input(client, input_str)
            if not success:
                log("Command unsuccessful", LOG_INFO)

        except Exit:
            break

    log("Exiting", LOG_INFO)


if __name__ == "__main__":
    main()
