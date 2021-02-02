from util_server import *
from connection_acceptor import ConnectionAcceptor
from packet_handler import PacketHandler
from packet_sender import PacketSender
from table import Table


class Server:
    def __init__(self):
        self.connection_acceptor = None
        self.client_listeners = []
        self.connections_players = {}
        self.incoming_packets = Queue()  # (packet, connection)
        self.outgoing_packets = Queue()  # (packet, connection)
        self.tables = []

        self.reset_tables()
        self.start_connection_acceptor()
        self.start_packet_handler()
        self.start_packet_sender()

        log("Server init done")

    def get_player(self, username) -> dict:
        try:
            with open(f"players/{username}.json", "r") as f:
                player = json.load(f)

        except FileNotFoundError:
            return {}

        return player

    def incoming(self, packet, connection):
        self.incoming_packets.put((packet, connection))

    def outgoing(self, packet, connection):
        self.outgoing_packets.put((packet, connection))

    def print_tables(self):
        lines = ["Tables"]
        lines.extend([table for table in self.tables])

        log("\n".join(lines), LogLevel.INFO)

    def reset_tables(self, n_tables=5):
        for i in range(1, n_tables + 1):
            self.tables.append(Table(self, name=f"Table {i}"))

        log("Reset tables", LogLevel.INFO)

    def start_connection_acceptor(self):
        if self.connection_acceptor is not None:
            log("Client acceptor already set, ignoring call", LogLevel.WARN)
            return

        self.connection_acceptor = ConnectionAcceptor(self)
        self.connection_acceptor.start()

    def start_packet_handler(self):
        packet_handler = PacketHandler(self)
        packet_handler.start()

    def start_packet_sender(self):
        packet_sender = PacketSender(self)
        packet_sender.start()
