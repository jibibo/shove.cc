from convenience import *
from user import User
from account import Account
from room import Room
from games.coinflip import Coinflip


_ = [("a", 100000), ("b", 200000), ("c", 300000), ("d", 400000)]
ACCOUNTS = [Account(username=u, password="1", money=m) for u, m in _]


def get_all_accounts():  # should be a generator if many files
    return ACCOUNTS

    # for filename in os.listdir(f"{os.getcwd()}/backend/accounts"):
    #     if os.path.isfile(f"{os.getcwd()}/backend/accounts/{filename}"):
    #         with open(f"{os.getcwd()}/backend/accounts/{filename}", "r") as f:
    #             try:
    #                 data = json.load(f)
    #             except BaseException as ex:
    #                 Log.fatal(f"UNHANDLED {type(ex).__name__}", exception=ex)
    #                 continue
    #
    #             all_account_data.append(data)


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

        self.reset_rooms()
        # self.rooms[0].add_bot(3)
        # for i in range(1):
        #     self.rooms[0].events.put("start")

        Log.info("Shove initialized")

    @staticmethod
    def get_account(**k_v) -> Account:
        Log.trace(f"Getting account with k_v: {k_v}")

        if len(k_v) != 1:
            raise ValueError(f"invalid k_v length: {len(k_v)}")

        k, v = list(k_v.items())[0]
        for account_data in get_all_accounts():
            if account_data[k] == v:
                Log.trace(f"Account matched: {account_data}")
                return account_data

        Log.trace(f"No account matched with k_v: {k_v}")

    def get_room_names(self) -> List[str]:
        return [room.name for room in self.get_rooms()]

    def get_rooms(self) -> List[Room]:
        return self._rooms.copy()

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
            Log.trace(f"Users in {room}: {room.get_users()}")
            if user in room.get_users():
                return room

        Log.trace("User is not in a room")

    def get_user(self, **k_v) -> User:
        Log.trace(f"Getting user with k_v: {k_v}")

        if len(k_v) != 1:
            raise ValueError(f"invalid k_v length: {len(k_v)}")

        k, v = list(k_v.items())[0]
        for user in self.get_all_users():
            if user.account and user.account[k] == v:
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

    def new_user_from_sid(self, sid: str):
        sids = [user.sid for user in self._users]
        if sid in sids:
            raise ValueError(f"SID already exists: {sid}")  # shouldn't ever happen

        user = User(sid)
        self._users.append(user)
        return user

    def on_connect(self, sid: str):
        user = self.new_user_from_sid(sid)
        if not user:
            return

        self.send_packet(user, "user_connected", {
            "you": True,
            "sid": sid,
            "user_count": self.get_user_count()
        })

        self.send_packet(self.get_all_users(), "user_connected", {
            "you": False,
            "sid": sid,
            "user_count": self.get_user_count()
        }, skip=user)

    def on_disconnect(self, sid: str):
        user = self.get_user_from_sid(sid=sid)
        if not user:
            return

        self._users.remove(user)

        self.send_packet(self.get_all_users(), "user_disconnected", {
            "sid": sid,
            "user_count": self.get_user_count()
        })

    def reset_rooms(self, n_rooms=3):
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

            if not users:
                Log.trace(f"Skipping outgoing {'response' if is_response else 'packet'} '{model}' with no recipients\n packet: {packet}")
                return

            self.outgoing_packets_queue.put((users, model, packet, is_response))

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on send_packet", ex)
