from convenience import *
from client import Client
from room import Room
from games.holdem import Holdem


def get_all_account_data():  # should be a generator if many files
    all_account_data = []
    Log.test("get_all_account_data()")
    for filename in os.listdir(f"{os.getcwd()}/backend/accounts"):
        if os.path.isfile(f"{os.getcwd()}/backend/accounts/{filename}"):
            with open(f"{os.getcwd()}/backend/accounts/{filename}", "r") as f:
                try:
                    data = json.load(f)
                except BaseException as ex:
                    Log.fatal(f"UNHANDLED {type(ex).__name__}", exception=ex)
                    continue

                all_account_data.append(data)

    return all_account_data


class Shove:
    def __init__(self, socketio):
        Log.trace("Initializing Shove")
        self.socketio = socketio

        self.clients: List[Client] = []
        # self.incoming_packets_queue = Queue()  # (Client, packet: dict)
        self.outgoing_packets_queue = Queue()  # ([Client], model: str, packet: dict, is_response: bool)

        self.default_game = Holdem
        self.next_bot_number = 1
        self.rooms: List[Room] = []
        self.reset_rooms()
        # self.rooms[0].add_bots(4)
        # for i in range(0):
        #     self.rooms[0].events.put("start")

        self.selected_table = None

        Log.info("Shove initialized")

    @staticmethod
    def get_account_data(**k_v) -> dict:
        if len(k_v) != 1:
            Log.error(f"Invalid k, v length: {k_v}")

        k, v = list(k_v.items())[0]
        for account_data in get_all_account_data():
            Log.test(account_data)
            if account_data[k] == v:
                Log.trace(f"Account data {account_data} matched with {k}={v}")
                return account_data

        Log.trace(f"No account data matched with {k}={v}")

    def get_all_clients(self):
        return self.clients.copy()

    def get_all_room_names(self):
        return [room.name for room in self.rooms]

    def get_client(self, sid: str) -> Client:
        for client in self.clients:
            if client.sid == sid:
                return client

        Log.warn(f"Could not find client with sid {sid}")

    def get_clients_count(self):
        return len(self.clients)

    def get_default_game(self):
        return self.default_game

    def get_next_bot_number(self) -> int:
        old = self.next_bot_number
        self.next_bot_number += 1
        return old

    def get_room(self, room_name: str) -> Room:
        room_name_formatted = room_name.lower().strip()
        for room in self.rooms:
            if room.name.lower() == room_name_formatted:
                Log.trace(f"Found room with matching name: {room}")
                return room

        Log.trace("Room with matching name not found")

    def new_client(self, sid: str):
        sids = [client.sid for client in self.clients]
        if sid in sids:
            Log.error(f"Attempted to create new client with existing sid {sid}")  # SHOULDN'T happen
            return

        client = Client(sid)
        self.clients.append(client)
        return client

    def on_connect(self, sid: str):
        client = self.new_client(sid)
        if not client:
            return

        self.send_queue(client, "client_connected", {
            "you": True,
            "sid": sid,
            "online_count": len(self.clients)
        })
        self.send_queue(self.get_all_clients(), "client_connected", {
            "you": False,
            "sid": sid,
            "online_count": len(self.clients)
        }, skip=client)

    def on_disconnect(self, sid: str):
        client = self.get_client(sid)
        if not client:
            return

        self.clients.remove(client)

        self.send_queue(self.get_all_clients(), "client_disconnected", {
            "sid": sid,
            "online_count": len(self.clients)
        })

    def print_rooms(self):
        lines = ["Rooms"]
        lines.extend([f"{room}" for room in self.rooms])
        Log.info("\n".join(lines))

    def reset_rooms(self, n_rooms=1):
        Log.info("Resetting rooms")
        self.rooms = []  # todo handle removing clients from room
        for _ in range(n_rooms):
            self.rooms.append(Room(self))

    def send_queue(self, clients: Union[Client, list], model: str, packet: dict, skip: Client = None, is_response=False):
        try:
            if type(clients) == Client:
                clients = [clients]

            elif type(clients) == list:
                if clients and type(clients[0]) != Client:
                    raise ValueError(f"List does not contain 'Client' object(s) but {type(clients[0])}")

            else:
                raise ValueError(f"Invalid 'clients' type: {type(clients)}")

            if skip and skip in clients:
                clients.remove(skip)

            if not clients:
                Log.trace(f"Skipping outgoing {model} packet with no recipients: {packet} ")
                return

            self.outgoing_packets_queue.put((clients, model, packet, is_response))

        except ValueError as ex:
            Log.error("Internal error on adding outgoing packet to queue", exception=ex)

        except BaseException as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on adding outgoing packet to queue", exception=ex)
