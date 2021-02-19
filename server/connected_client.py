from server_util import *


class ConnectedClient:
    def __init__(self, server, connection, address):
        self.server = server
        self.connection: socket.socket = connection
        self.address = address
        self.player = None  # todo make this Account with money, name, password; each game has unique player class
        self.send({
            "model": "connected"
        })
        log(f"{self.address[0]}:{self.address[1]} connected")
        threading.Thread(target=self.listen, name=f"ClientListener/{self.address[0]}:{self.address[1]}", daemon=True)

    def listen(self):
        log("Listener ready")

        while True:
            try:
                packet = self.receive_and_convert_packet()
                self.server.received_client_packets.put((self, packet))

            except InvalidPacket as ex:
                log(f"Invalid packet received: {ex.details}", LOG_WARN, ex)
                continue

            except LostConnection as ex:
                log(f"Lost connection: {ex.reason}", LOG_INFO)
                break

            except Exception as ex:
                log(f"UNHANDLED {type(ex).__name__} on receiving/converting packet", LOG_ERROR, ex)
                continue

        log("Listener stopped")

    def logged_in(self, player):
        self.player = player

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

    def send(self, packet: dict):
        self.server.outgoing_packets.put((self.connection, packet))
