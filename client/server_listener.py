from util_client import *


class ServerListener(threading.Thread):
    def __init__(self, client):
        self.client = client
        self.address = SERVER_ADDRESS
        self.reconnect = True
        self.attempts = 0

        super().__init__(name=f"ServerListener", daemon=True)

    def run(self):
        while self.reconnect:
            self.attempts += 1

            if self.client.socket is None:
                self.connect()

            if self.attempts == CONNECT_ATTEMPTS:
                log("Maximum attempts reached")
                break

        self.client.server_listener = None
        log("Set server_listener to None")

    def connect(self):
        self.client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = self.address
        log(f"Connecting to {host}:{port}, attempt {self.attempts}", LogLevel.INFO)

        try:
            self.client.socket.connect(SERVER_ADDRESS)

        except ConnectionRefusedError as ex:
            log(f"Failed to connect to server: {ex.strerror}", LogLevel.INFO)

        else:
            log(f"Connected! Now receiving packets", LogLevel.INFO)
            self.client.connected()
            self.attempts = 0

            while True:
                try:
                    self.receive_and_handle_packets()

                except LostConnection as ex:
                    log(f"Lost connection to server: {ex.reason}", LogLevel.INFO)
                    break

                except BaseException as ex:
                    log(f"Unhandled {type(ex).__name__} on receive and handle: {ex}", LogLevel.ERROR)
                    break

        self.client.socket = None

    def receive_and_handle_packets(self):
        try:  # receive header
            header_bytes = self.client.socket.recv(HEADER_SIZE)

        except OSError as ex:
            raise LostConnection(ex.strerror)

        except ConnectionResetError as ex:
            raise LostConnection(ex.strerror)

        except BaseException:
            log("Unhandled exception on receiving header", LogLevel.ERROR)
            raise

        try:  # convert header
            header = int(header_bytes)

        except ValueError as ex:
            log(f"Exception on converting header: {ex}", LogLevel.WARN)
            return

        log(f"Received header: {header}")

        try:  # receive packet
            packet_bytes = self.client.socket.recv(header)

        except ConnectionResetError as ex:
            raise LostConnection(ex.strerror)

        except BaseException:
            log("Unhandled exception on receiving packet", LogLevel.ERROR)
            raise

        try:  # convert packet
            packet_str = str(packet_bytes, encoding="utf-8")
            packet = json.loads(packet_str)

        except json.JSONDecodeError as ex:
            log(f"Exception on converting packet: {ex}", LogLevel.WARN)
            return

        except BaseException:
            log("Unhandled exception on converting packet", LogLevel.ERROR)
            raise

        log(f"Received packet: {packet}")
        self.handle_packet(packet)  # todo try except

    def handle_packet(self, packet: dict):
        assert "model" in packet.keys(), "no model set"

        model = packet["model"]

        if model == "connected":
            return

        if model == "logged_in":
            return

        raise UnknownPacketModel