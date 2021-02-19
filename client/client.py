from client_util import *
from server_listener import ServerListener


class Client:
    def __init__(self):
        log("Client init...")
        self.socket: socket.socket = None
        self.server_listener = ServerListener(self)
        self.server_listener.start()

        self.username = "bob"
        self.password = "123"
        log("Client init done")

    def connected(self):
        self.send({
            "model": "log_in",
            "username": self.username,
            "password": self.password
        })

    def send(self, packet: dict):
        try:
            packet_str = json.dumps(packet)
            header = f"{len(packet_str):<{HEADER_SIZE}}"
            self.socket.send(bytes(header + packet_str, encoding="utf-8"))

            log(f"Sent packet: {packet}")

        except BaseException as ex:
            log(f"UNHANDLED {type(ex).__name__} on sending packet", LOG_ERROR, traceback_print=True)

