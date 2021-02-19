from server_util import *

from packet_handler import PacketHandler
from packet_sender import PacketSender
from table import Table
from games.poker.poker import Poker
from connected_client import ConnectedClient


class Server:
    def __init__(self):
        log("Server init...")

        self.default_game = Poker
        self.tables: List[Table] = []
        self.reset_tables()
        self.tables[0].add_bots(2)

        self.socket: socket.socket = None
        self.connected_clients: List[ConnectedClient] = []
        self.received_client_packets = Queue()  # (ConnectedClient, packet)
        self.outgoing_client_packets = Queue()  # (ConnectedClient, packet)

        self.start_packet_sender()
        self.start_packet_handler()
        self.start_connection_acceptor()

        log("Server init done")

    @staticmethod
    def get_player(username) -> dict:  # todo messy exceptions
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
        log("Resetting tables...", LOG_INFO)
        self.tables = []  # todo handle removing clients from table
        for _ in range(n_tables):
            self.tables.append(Table(self))

    def send_multiple(self, connections: list, packet):  # todo del
        for connection in connections:
            self.outgoing_client_packets.put((connection, packet))

    def start_connection_acceptor(self):
        threading.Thread(target=self.accept_connections, name="ConnectionAcceptor", daemon=True).start()

    def accept_connections(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER_HOST, SERVER_PORT))
        self.socket.listen(SERVER_BACKLOG)
        log(f"Ready on {SERVER_HOST}:{SERVER_PORT}", LOG_INFO)

        while True:
            connection, address = self.socket.accept()
            connected_client = ConnectedClient(self, connection, address)
            self.connected_clients.append(connected_client)

    def start_packet_handler(self):
        PacketHandler(self).start()

    def start_packet_sender(self):
        PacketSender(self).start()
