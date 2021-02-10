from util_server import *
from connection_acceptor import ConnectionAcceptor
from packet_handler import PacketHandler
from packet_sender import PacketSender
from table import Table


class Server:
    def __init__(self):
        log("Server init...")
        self.client_listener_threads = []
        self.connections_players = {}
        self.incoming_packets = Queue()  # (packet, connection)
        self.outgoing_packets = Queue()  # (packet, connection)
        self.tables = []

        self.reset_tables()
        self.tables[0].add_bots(2)
        self.start_packet_sender()
        self.start_packet_handler()
        self.start_connection_acceptor()

        log("Server init done")

    def get_player(self, username) -> dict:
        try:
            with open(f"players/{username}.json", "r") as f:
                player = json.load(f)

        except FileNotFoundError:
            return {}

        return player

    def print_tables(self):
        lines = ["Tables"]
        lines.extend([table for table in self.tables])
        log("\n".join(lines), LOG_INFO)

    def reset_tables(self, n_tables=2):
        log("Resetting tables", LOG_INFO)
        self.tables = []  # todo handle removing clients from table
        for i in range(1, n_tables + 1):
            self.tables.append(Table(self, name=f"Table {i}"))

    def send_multiple(self, connections: list, packet):
        for connection in connections:
            self.outgoing_packets.put((connection, packet))

    def send_single(self, connection, packet):
        self.outgoing_packets.put((connection, packet))

    def start_connection_acceptor(self):
        connection_acceptor_thread = ConnectionAcceptor(self)
        connection_acceptor_thread.start()

    def start_packet_handler(self):
        packet_handler = PacketHandler(self)
        packet_handler.start()

    def start_packet_sender(self):
        packet_sender = PacketSender(self)
        packet_sender.start()
