from util_server import *


class ClientListener(threading.Thread):
    def __init__(self, server, connection, address):
        self.server = server
        self.connection: socket.socket = connection
        self.address = address

        super().__init__(name=f"ClientListener/{address[0]}:{address[1]}", daemon=True)

    def run(self):
        self.server.send_single(self.connection, {
            "model": "connected"
        })

        log("Ready")

        while True:
            try:
                packet = self.receive_and_convert_packet()
                self.server.incoming_packets.put((self.connection, packet))

            except InvalidPacket as ex:
                log(f"Invalid packet received", LOG_WARN, traceback_print=True)
                continue

            except LostConnection as ex:
                log(f"Lost connection: {ex.reason}", LOG_INFO)
                break

            except BaseException as ex:
                log(f"UNHANDLED {type(ex).__name__} on receiving/converting packet", LOG_ERROR, traceback_print=True)
                continue

        self.server.client_listener_threads.remove(self)
        log("Thread exiting run()")

    def receive_and_convert_packet(self) -> dict:
        try:
            header_bytes = self.connection.recv(HEADER_SIZE)
            header = int(header_bytes)
            log(f"Received header: {header}")
            packet_bytes = self.connection.recv(header)
            packet_str = str(packet_bytes, encoding="utf-8")
            log(f"Received packet, raw: {packet_str}")
            packet = json.loads(packet_str)
            return packet

        except ValueError as ex:  # includes JSONDecodeError
            raise InvalidPacket(ex)

        except ConnectionResetError as ex:
            raise LostConnection(ex.strerror)
