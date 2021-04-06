from convenience import *

from user import User, FakeUser
from account import Account
from room import Room

from games.coinflip import Coinflip


ACCOUNTS = [Account(username=u, password="1", money=m)
            for u, m in [("a", 100000), ("badr", 77777777778), ("jim", 420000)]]


class Shove:
    def __init__(self, sio):
        Log.trace("Initializing Shove")
        self.sio: socketio.Server = sio
        self.incoming_packets_queue = Queue()  # (User, model, packet, packet_number)
        self.outgoing_packets_queue = Queue()  # ([User], model, packet, skip, is_response)

        self._default_game = Coinflip
        self._next_bot_number = 0
        self._next_packet_number = 0
        self._users: List[User] = []
        self._rooms: List[Room] = []

        self.reset_rooms(2)
        # self.rooms[0].add_bot(3)
        for i in range(1):
            self.get_rooms()[0].try_to_start_game()

        if PRIVATE_ACCESS:
            Log.trace("Initializing Trello client, fetching card list")
            client = TrelloClient(
                api_key=TRELLO_API_KEY,
                api_secret=TRELLO_API_SECRET,
                token=TRELLO_TOKEN
            )
            board = client.get_board("603c469a39b5466c51c3a176")
            self._trello_card_list = board.get_list("60587b1f02721f0c7b547f5b")
        else:
            Log.trace("No private access, not initializing Trello client")

        # non-subprocess version of YT DL
        # youtube_dl_options = {
        #     "download_archive": f"{CWD_PATH}/backend/audio_cache/archive.txt",
        #     "verbose": True,
        #     "listformats": True,
        #     "prefer_ffmpeg": True,
        # }
        # self.youtube_dl = youtube_dl.YoutubeDL(youtube_dl_options)
        # self.youtube_dl.download([f"https://youtube.com/watch?v={youtube_id}"])

        self.latest_audio_url = None
        self.latest_audio_author = None
        self.audio_urls_cached = []

        Log.test("Faking play packet")
        fake_link = "XwxLwG2_Sxk"
        self.incoming_packets_queue.put((FakeUser(), "send_message", {
            "message": f"/play {fake_link}"
        }, -1))
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

    def on_connect(self, sid: str) -> User:
        user = self.create_new_user_from_sid(sid)
        if not user:
            raise ValueError("No User object provided")

        self.send_packet_to(user, "user_connected", {
            "you": True,
            "users": [user.get_account_data_copy()
                      for user in self.get_all_users() if user.is_logged_in()],
            "user_count": self.get_user_count()
        })

        self.send_packet_to_everyone("user_connected", {
            "you": False,
            "users": [user.get_account_data_copy()
                      for user in self.get_all_users() if user.is_logged_in()],
            "user_count": self.get_user_count()
        }, skip=user)

        return user

    def on_disconnect(self, sid: str):  # todo disconnect reasons
        user = self.get_user_from_sid(sid=sid)
        if not user:
            raise ValueError(f"shove.on_disconnect: user with SID {sid} does not exist")

        room = self.get_room_of_user(user)
        if room:
            room.user_leave(user)

        self._users.remove(user)

        self.send_packet_to_everyone("user_disconnected", {
            "username": user.get_username(),
            "users": [user.get_account_data_copy()
                      for user in self.get_all_users() if user.is_logged_in()],
            "user_count": self.get_user_count()
        })

    def reset_rooms(self, n_rooms=5):
        Log.info("Resetting rooms")
        self._rooms = []  # todo handle removing users from room
        for _ in range(n_rooms):
            self._rooms.append(Room(self))

    def send_packet_to(self, users: Union[User, List[User]], model: str, packet: dict, skip: Union[User, List[User]] = None, is_response=False):
        self.outgoing_packets_queue.put((users, model, packet, skip, is_response))

    def send_packet_to_everyone(self, model: str, packet: dict, skip: Union[User, List[User]] = None):
        self.send_packet_to(self.get_all_users(), model, packet, skip)
