from util_server import *


class ClientListener(threading.Thread):
    def __init__(self, server, connection, address):
        self.server = server
        self.connection: socket.socket = connection
        self.address = address

        super().__init__(name=f"ClientListener/{address[0]}:{address[1]}", daemon=True)

    def run(self):
        log("Now listening")
        self.server.outgoing(self.connection, {
            "model": "connected"
        })

        while True:
            try:
                self.receive()

            except LostConnection as ex:
                log(f"Lost connection: {ex.reason}", LogLevel.INFO)
                break

            except BaseException as ex:
                log(f"Unhandled {type(ex).__name__} on receive: {ex}", LogLevel.ERROR)
                break

        self.server.client_listeners.remove(self)

    def receive(self):
        try:  # receive header
            header_bytes = self.connection.recv(HEADER_SIZE)

        except ConnectionResetError as ex:
            raise LostConnection(ex.strerror)

        except BaseException as ex:
            log("Unhandled exception on receiving header", LogLevel.ERROR)
            raise ex

        try:  # convert header
            header = int(header_bytes)

        except ValueError:
            log(f"Invalid header received: {header}", LogLevel.ERROR)
            return

        except BaseException as ex:
            log("Unhandled exception on converting header", LogLevel.ERROR)
            raise ex

        log(f"Received header: {header}")

        try:  # receive packet
            packet_bytes = self.connection.recv(header)

        except ConnectionResetError as ex:
            raise LostConnection(ex.strerror)

        except BaseException as ex:
            log("Unhandled exception on receiving packet", LogLevel.ERROR)
            raise ex

        try:  # convert packet
            packet_str = str(packet_bytes, encoding="utf-8")
            packet = json.loads(packet_str)

        except BaseException as ex:
            log("Unhandled exception on converting packet", LogLevel.ERROR)
            raise ex

        log(f"Received packet: {packet}")
        self.server.incoming(self.connection, packet)
