from convenience import *

from user import User
from account import Account
from room import Room

from games.coinflip import Coinflip


ACCOUNTS = [Account(username=u, password="1", money=m)
            for u, m in [("a", 100000), ("b", 200000), ("c", 300000), ("d", 400000), ("badr", 200), ("jul", 777777), ("jim", 420000)]]


# def get_all_accounts():  # should be a generator if many files
#     return ACCOUNTS
#
#     for filename in os.listdir(f"{os.getcwd()}/backend/accounts"):
#         if os.path.isfile(f"{os.getcwd()}/backend/accounts/{filename}"):
#             with open(f"{os.getcwd()}/backend/accounts/{filename}", "r") as f:
#                 try:
#                     data = json.load(f)
#                 except BaseException as ex:
#                     Log.fatal(f"UNHANDLED {type(ex).__name__}", exception=ex)
#                     continue
#
#                 all_account_data.append(data)


class Shove:
    def __init__(self, socketio):
        Log.trace("Initializing Shove")
        self.socketio = socketio

        self.incoming_packets_queue = Queue()  # (User, model, packet)
        self.outgoing_packets_queue = Queue()  # ([User], model, packet, is_response)

        self._default_game = Coinflip
        self._next_bot_number = 0
        self._next_packet_number = 0
        self._users: List[User] = []
        self._rooms: List[Room] = []

        self.reset_rooms(2)
        # self.rooms[0].add_bot(3)
        # for i in range(1):
        #     self.rooms[0].events.put("start")

        Log.trace("Initializing Trello client, fetching card list")
        client = TrelloClient(
            api_key=TRELLO_API_KEY,
            api_secret=TRELLO_API_SECRET,
            token=TRELLO_TOKEN
        )
        board = client.get_board("603c469a39b5466c51c3a176")
        self._trello_card_list = board.get_list("60587b1f02721f0c7b547f5b")

        self.awaiting_pong_users: List[User] = []

        Log.trace("Shove initialized")

    def add_trello_card(self, name, description=None):
        name = name.strip()
        if description is not None:
            description = description.strip()

        Log.trace(f"Adding card to Trello card list, name = '{name}', description = '{description}'")
        self._trello_card_list.add_card(name=name, desc=description, position="top")
        Log.trace(f"Added card")

    def create_random_account(self):
        return

    def create_new_user_from_sid(self, sid: str):
        sids = [user.sid for user in self._users]
        if sid in sids:
            raise ValueError(f"SID already exists: {sid}")  # shouldn't ever happen

        user = User(sid)
        self._users.append(user)
        return user

    def disconnect_awaiting_pong_users(self):
        for user in self.awaiting_pong_users:
            Log.warn(f"Disconnecting user {user} (didn't pong)")
            self.on_disconnect(user.sid)

    def get_account(self, fail_silently=False, **k_v) -> Account:  # todo support for multiple kwargs
        Log.trace(f"Trying to get account with k_v: {k_v}")

        if len(k_v) != 1:
            raise ValueError(f"Invalid k_v length: {len(k_v)}")

        k, v = list(k_v.items())[0]
        for account in self.get_all_accounts():
            if account[k] == v:
                Log.trace(f"Account match with k_v: {account}")
                return account

        if fail_silently:
            Log.trace(f"No account matched with k_v: {k_v}")
        else:
            raise AccountNotFound

    def get_room_names(self) -> List[str]:
        return [room.name for room in self.get_rooms()]

    def get_rooms(self) -> List[Room]:
        return self._rooms.copy()

    @staticmethod
    def get_all_accounts() -> List[Account]:
        return ACCOUNTS.copy()

    def get_all_users(self) -> List[User]:
        return self._users.copy()

    def get_default_game(self):
        return self._default_game

    def get_next_bot_number(self) -> int:
        self._next_bot_number += 1
        return self._next_bot_number

    def get_next_packet_number(self) -> int:
        self._next_packet_number += 1
        return self._next_packet_number

    def get_room(self, room_name: str) -> Room:
        Log.trace(f"Getting room with name: '{room_name}'")
        room_name_formatted = room_name.lower().strip()
        for room in self.get_rooms():
            if room.name.lower() == room_name_formatted:
                Log.trace(f"Found room with matching name: {room}")
                return room

        Log.trace("Room with matching name not found")

    def get_room_count(self) -> int:
        return len(self.get_rooms())

    def get_room_of_user(self, user: User) -> Room:
        Log.trace(f"Getting room of user {user}")

        for room in self.get_rooms():
            if user in room.get_users():
                Log.trace(f"User is in room: {room}")
                return room

        Log.trace("User is not in a room")

    def get_user(self, **k_v) -> User:
        Log.trace(f"Getting user with k_v: {k_v}")

        if len(k_v) != 1:
            raise ValueError(f"Invalid k_v length: {len(k_v)}")

        k, v = list(k_v.items())[0]
        for user in self.get_all_users():
            if user.is_logged_in() and user.get_account_data_copy()[k] == v:
                Log.trace(f"User matched: {user}")
                return user

        Log.trace(f"No user matched with k_v: {k_v}")

    def get_user_from_sid(self, sid) -> User:
        for user in self.get_all_users():
            if user.sid == sid:
                return user

        Log.warn(f"No user matched with SID: {sid}")

    def get_user_count(self) -> int:
        return len(self._users)

    def on_connect(self, sid: str):
        user = self.create_new_user_from_sid(sid)
        if not user:
            return

        self.send_packet(user, "user_connected", {
            "you": True,
            "users": [user.get_account_data_copy()
                      for user in self.get_all_users() if user.is_logged_in()],
            "user_count": self.get_user_count()
        })

        self.send_packet_all("user_connected", {
            "you": False,
            "users": [user.get_account_data_copy()
                      for user in self.get_all_users() if user.is_logged_in()],
            "user_count": self.get_user_count()
        }, skip=user)

    def on_disconnect(self, sid: str):
        user = self.get_user_from_sid(sid=sid)
        if not user:
            raise ValueError(f"shove.on_disconnect: user with SID {sid} does not exist")

        room = self.get_room_of_user(user)
        if room:
            room.user_leave(user)

        self._users.remove(user)

        self.send_packet_all("user_disconnected", {
            "username": user.get_username(),
            "users": [user.get_account_data_copy()
                      for user in self.get_all_users() if user.is_logged_in()],
            "user_count": self.get_user_count()
        })

    def ping_all_users(self):
        Log.trace("Pinging all users")
        now = int(time.time() * 1000)
        for user in self.get_all_users():
            user.pinged_timestamp = now
        self.awaiting_pong_users = self.get_all_users()
        self.send_packet_all("ping", {})

    def reset_rooms(self, n_rooms=5):
        Log.info("Resetting rooms")
        self._rooms = []  # todo handle removing users from room
        for _ in range(n_rooms):
            self._rooms.append(Room(self))

    def send_packet(self, users: Union[User, List[User]], model: str, packet: dict, skip: Union[User, List[User]] = None, is_response=False):
        try:
            if type(users) == User:
                users = [users]

            elif type(users) == list:
                if users and type(users[0]) != User:
                    raise ValueError(f"'users' does not contain 'User' object(s), but: {type(users[0])}")

            else:
                raise ValueError(f"Invalid 'users' type: {type(users)}")

            if skip:
                if type(skip) == User:
                    skip = [skip]

                elif type(skip) == list:
                    if skip and type(skip[0]) != User:
                        raise ValueError(f"'skip' does not contain 'User' object(s), but: {type(users[0])}")

                else:
                    raise ValueError(f"Invalid 'skip' type: {type(users)}")

                for skip_user in skip:
                    users.remove(skip_user)

            if users:
                self.outgoing_packets_queue.put((users, model, packet, is_response))

            else:
                Log.trace(f"Skipped outgoing {'response' if is_response else 'packet'} '{model}' with no recipients\n packet: {packet}")

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on shove.send_packet", ex)

    def send_packet_all(self, model: str, packet: dict, skip: Union[User, List[User]] = None):
        self.send_packet(self.get_all_users(), model, packet, skip)
