from client_util import *


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
                log("Maximum connect attempts reached", LOG_INFO)
                break

        self.client.server_listener = None
        log("Thread exiting run()")

    def connect(self):
        self.client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = self.address
        log(f"Connecting to {host}:{port}, attempt {self.attempts}", LOG_INFO)

        try:
            self.client.socket.connect(SERVER_ADDRESS)

        except ConnectionRefusedError as ex:
            log(f"Failed to connect to server: {ex.strerror}", LOG_INFO)

        except BaseException as ex:
            log(f"UNHANDLED {type(ex).__name__} on connecting", LOG_ERROR, traceback_print=True)

        else:
            log(f"Connected! Now receiving packets", LOG_INFO)
            self.client.connected()
            self.attempts = 0

            while True:
                try:  # receive and convert header + packet
                    packet = self.receive_and_convert_packet()

                except InvalidPacket as ex:
                    log(f"Invalid packet: {ex.details}", LOG_WARN)
                    continue

                except LostConnection as ex:
                    log(f"Lost connection to server: {ex.reason}", LOG_INFO)
                    break

                except BaseException as ex:
                    log(f"UNHANDLED {type(ex).__name__} on receiving/converting packet", LOG_ERROR, traceback_print=True)
                    break

                try:  # handle the converted packet
                    self.handle_packet(packet)
                    log(f"Handled packet: {packet}")

                except BaseException as ex:
                    log(f"UNHANDLED {type(ex).__name__} on handling packet", LOG_ERROR, traceback_print=True)
                    break

        self.client.socket = None  # setting this to None every connect() required?

    def receive_and_convert_packet(self) -> dict:
        try:
            header_bytes = self.client.socket.recv(HEADER_SIZE)
            header = int(header_bytes)
            log(f"Received header: {header}")
            packet_bytes = self.client.socket.recv(header)
            packet_str = str(packet_bytes, encoding="utf-8")
            log(f"Received packet, raw: {packet_str}")
            packet = json.loads(packet_str)
            return packet

        except ValueError as ex:  # includes JSONDecodeError
            raise InvalidPacket(f"{type(ex).__name__}: {ex}")

        except (OSError, ConnectionResetError) as ex:
            raise LostConnection(ex.strerror)

    def handle_packet(self, packet: dict):
        if "model" not in packet:
            raise InvalidPacket(f"No model set")

        model = packet["model"]

        if model == "connected":
            return

        if model == "logged_in":
            return

        raise InvalidPacket(f"Invalid model '{model}'")