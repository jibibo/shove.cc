from util import *
from client import Client
from table import Table
from games.holdem import Holdem


class Server:
    def __init__(self, socketio):
        Log.debug("Setting up server")
        self.socketio = socketio

        self.clients: List[Client] = []
        self.incoming_packets_queue = Queue()  # (Client, packet)
        self.outgoing_packets_queue = Queue()  # ([Client], packet, is_response)

        self.default_game = Holdem
        self.next_bot_number = 1
        self.tables: List[Table] = []
        self.reset_tables()
        # self.tables[0].add_bots(4)
        # for i in range(0):
        #     self.tables[0].events.put("start")

        self.selected_table = None

        Log.info("Server ready")

    def get_client(self, sid: str) -> Client:
        for client in self.clients:
            if client.sid == sid:
                return client

        Log.warn(f"Could not find client with sid {sid}")

    def get_all_clients(self):
        return self.clients.copy()

    def get_clients_count(self):
        return len(self.clients)

    def get_default_game(self):
        return self.default_game

    def get_next_bot_number(self) -> int:
        old = self.next_bot_number
        self.next_bot_number += 1
        return old

    # @staticmethod
    # def get_player(username) -> dict:  # todo should just lookup accounts
    #     try:
    #         with open(f"players/{username}.json", "r") as f:
    #             player = json.load(f)
    #
    #     except FileNotFoundError:
    #         return {}
    #
    #     return player

    def get_table(self, find_table: str) -> Table:
        find_table_lower = find_table.lower()
        for table in self.tables:
            if table.name.lower() == find_table_lower:
                Log.trace("Found table with matching name")
                return table

        Log.trace("Table with matching name not found")

    def new_client(self, sid: str):
        sids = [client.sid for client in self.clients]
        if sid in sids:
            Log.warn(f"Attempted to create client with existing sid {sid}")  # SHOULDN'T happen
            return

        client = Client(sid)
        self.clients.append(client)
        return client

    def on_connect(self, sid: str):
        client = self.new_client(sid)
        if not client:
            return

        self.send_packet(client, {
            "model": "client_connected",
            "you": True,
            "sid": sid,
            "online_count": len(self.clients)
        })
        self.send_packet(self.get_all_clients(), {
            "model": "client_connected",
            "you": False,
            "sid": sid,
            "online_count": len(self.clients)
        }, skip=client)

    def on_disconnect(self, sid: str):
        client = self.get_client(sid)
        if not client:
            return

        self.clients.remove(client)

        self.send_packet(self.get_all_clients(), {
            "model": "client_disconnected",
            "sid": sid,
            "online_count": len(self.clients)
        })

    def print_tables(self):
        lines = ["Tables"]
        lines.extend([f"{table}" for table in self.tables])
        Log.info("\n".join(lines))

    def reset_tables(self, n_tables=1):
        Log.info("Resetting tables")
        self.tables = []  # todo handle removing clients from table
        for _ in range(n_tables):
            self.tables.append(Table(self))

    def send_packet(self, clients: Union[Client, list], packet: dict, skip: Client = None, is_response=False):
        try:
            if type(clients) == Client:
                clients = [clients]

            elif type(clients) == list:
                if clients and type(clients[0]) != Client:
                    raise ValueError(f"List does not contain 'Client' objects: {type(clients[0])}")

            else:
                raise ValueError(f"Invalid 'clients' type: {type(clients)}")

            if skip and skip in clients:
                clients.remove(skip)

            if not clients:
                Log.trace(f"Skipped outgoing {packet['model']} packet with no recipients")
                return

            self.outgoing_packets_queue.put((clients, packet, is_response))

            # sids = [client.sid for client in clients]
            # for sid in sids:
            #     self.socketio.send(packet, room=sid)
            # Log.debug(f"Sent '{packet['model']}' packet")

        except ValueError as ex:
            Log.error("Error on server.send_packet()", exception=ex)
