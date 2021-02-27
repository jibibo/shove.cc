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
        Log.info(f"{self.address[0]}:{self.address[1]} connected")
        threading.Thread(target=self.listen, name=f"ClientListener/{self.address[0]}:{self.address[1]}", daemon=True)

    def listen(self):
        Log.debug("Listener ready")

        while True:
            try:
                packet = self.receive_and_convert_packet()
                self.server.received_client_packets.put((self, packet))

            except InvalidPacket as ex:
                Log.error(f"Invalid packet received: {ex.details}", ex)
                continue

            except LostConnection as ex:
                Log.info(f"Lost connection: {ex.reason}")
                break

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on receiving/converting packet", ex)
                continue

        Log.debug("Listener stopped")

    def logged_in(self, player):
        self.player = player

    def receive_and_convert_packet(self) -> dict:
        try:
            header_bytes = self.connection.recv(HEADER_SIZE)
            header = int(header_bytes)
            Log.trace(f"Received header: {header}")
            packet_bytes = self.connection.recv(header)
            packet_str = str(packet_bytes, encoding="utf-8")
            Log.trace(f"Received packet, raw: {packet_str}")
            packet = json.loads(packet_str)
            return packet

        except ValueError as ex:  # includes JSONDecodeError
            raise InvalidPacket(ex)

        except ConnectionResetError as ex:
            raise LostConnection(ex.strerror)

    def send(self, packet: dict):
        self.server.outgoing_packets.put((self.connection, packet))
