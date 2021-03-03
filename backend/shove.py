from convenience import *
from client import Client
from room import Room
from games.holdem import Holdem


class Shove:
    def __init__(self, socketio):
        Log.trace("Initializing Shove")
        self.socketio = socketio

        self.clients: List[Client] = []
        self.incoming_packets_queue = Queue()  # (Client, packet: dict)
        self.outgoing_packets_queue = Queue()  # ([Client], packet: dict, is_response: bool)

        self.default_game = Holdem
        self.next_bot_number = 1
        self.rooms: List[Room] = []
        self.reset_rooms()
        # self.rooms[0].add_bots(4)
        # for i in range(0):
        #     self.rooms[0].events.put("start")

        self.selected_table = None

        Log.info("Shove initialized")

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

        self.send_queue(client, {
            "model": "client_connected",
            "you": True,
            "sid": sid,
            "online_count": len(self.clients)
        })
        self.send_queue(self.get_all_clients(), {
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

        self.send_queue(self.get_all_clients(), {
            "model": "client_disconnected",
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

    def send_queue(self, clients: Union[Client, list], packet: dict, skip: Client = None, is_response=False):
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

        except ValueError as ex:
            Log.error("Error on pending outgoing packet", exception=ex)

        except BaseException as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on pending outgoing packet", exception=ex)
