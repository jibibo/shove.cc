from server_util import *

from connected_client import ConnectedClient
from packet_handler_thread import PacketHandlerThread
from packet_sender_thread import PacketSenderThread
from table import Table
from games.holdem import Holdem


class Server:
    def __init__(self):
        Log.debug("Setting up server")

        self.default_game = Holdem
        self.selected_table = None
        self.next_bot_number = 1
        self.tables: List[Table] = []
        self.reset_tables()
        self.tables[0].add_bots(4)
        for i in range(20):
            self.tables[0].events.put("start")

        self.connected_clients: List[ConnectedClient] = []
        self.received_client_packets = Queue()  # (ConnectedClient, packet)
        self.outgoing_client_packets = Queue()  # (ConnectedClient, packet)

        self.start_packet_sender()
        self.start_packet_handler()
        self.start_connection_acceptor()

        Log.info("Server ready")

    def get_default_game(self):
        return self.default_game

    def get_next_bot_number(self) -> int:
        old = self.next_bot_number
        self.next_bot_number += 1
        return old

    @staticmethod
    def get_player(username) -> dict:  # todo messy exception handling
        try:
            with open(f"players/{username}.json", "r") as f:
                player = json.load(f)

        except FileNotFoundError:
            return {}

        return player

    def get_table(self, find_table: str) -> Table:
        find_table_lower = find_table.lower()
        for table in self.tables:
            if table.name.lower() == find_table_lower:
                Log.trace("Found table with matching name")
                return table

        Log.trace("Table with matching name not found")

    def print_tables(self):
        lines = ["Tables"]
        lines.extend([f"{table}" for table in self.tables])
        Log.info("\n".join(lines))

    def reset_tables(self, n_tables=1):
        Log.info("Resetting tables")
        self.tables = []  # todo handle removing clients from table
        for _ in range(n_tables):
            self.tables.append(Table(self))

    def send_multiple(self, connections: list, packet):  # todo del
        for connection in connections:
            self.outgoing_client_packets.put((connection, packet))

    def start_connection_acceptor(self):
        threading.Thread(target=self.accept_connections, name="ConnectionAcceptor", daemon=True).start()

    def accept_connections(self):  # todo handle possible exceptions/interruptions and retry
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind(("0.0.0.0", SERVER_PORT))
        except OSError as ex:
            Log.fatal(f"Failed to bind to port {SERVER_PORT}", ex)
            return

        server_socket.listen(SERVER_BACKLOG)
        Log.info(f"Ready on port {SERVER_PORT}")

        while True:
            connection, address = server_socket.accept()
            connected_client = ConnectedClient(self, connection, address)
            self.connected_clients.append(connected_client)

    def start_packet_handler(self):
        PacketHandlerThread(self).start()

    def start_packet_sender(self):
        PacketSenderThread(self).start()
