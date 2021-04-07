from convenience import *


# Astract classes

class AbstractDatabase(ABC):
    def __init__(self, filename):
        self._filename = filename
        self._file_abs = f"{CWD_PATH}/databases/{filename}"
        self._entries = set()

    def add_entry(self, entry):
        self._entries.add(entry)

    def find_multiple(self, raise_not_found: bool = True, **kwargs) -> set:
        Log.trace(f"Finding database entries with kwargs: {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        candidates = set()
        for entry in self._entries:
            if entry.matches_kwargs(**kwargs):
                candidates.add(entry)

        if candidates:
            return candidates
        elif raise_not_found:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No database entries found")

    def find_single(self, raise_not_found: bool = True, **kwargs):
        Log.trace(f"Finding database entry with kwargs: {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        for entry in self._entries:
            if entry.matches_kwargs(**kwargs):
                return entry

        if raise_not_found:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No database entry found")

    def get_entries(self) -> set:
        return self._entries

    @abstractmethod
    def get_entries_as_json(self) -> Union[dict, list]:
        pass

    @abstractmethod
    def load_entries_from_json(self, entries_as_json) -> set:
        pass

    def read_from_file(self):
        Log.trace(f"Reading from database {self._filename}")

        with open(self._filename, "r") as f:
            entries_as_json = json.load(f)

        self._entries = self.load_entries_from_json(entries_as_json)
        Log.trace(f"Read from database {self._filename}")

    def write_to_file(self):  # todo write to temp file while writing to prevent potential data loss during crashes (if needed?)
        Log.trace(f"Writing to database {self._filename}")

        data_as_json = self.get_entries_as_json()
        with open(self._filename, "w") as f:
            json.dump(data_as_json, f, indent=2)

        Log.trace(f"Wrote to database {self._filename}")


class AbstractDatabaseEntry(ABC):
    def __init__(self, database, default_data: dict, **kwargs):
        self._type_name = type(self).__name__

        for k, v in kwargs.items():
            if k not in default_data:
                raise ValueError(f"Unknown key for database entry type {self._type_name}: {k}={v}")

        self._data = default_data
        self._data.update(kwargs)

        self._database = database
        database.add_entry(self)

        Log.trace(f"Created database entry of type {self._type_name}: {self}")

    def __getitem__(self, key):
        try:
            return self._data[key]

        except KeyError as ex:
            Log.error(f"Invalid key for database entry type {self._type_name}: {key}", ex)

    def __repr__(self):
        return f"<Database entry of type {self._type_name}: {self}>"

    def __setitem__(self, key, value):
        try:
            old = self._data[key]
            self._data[key] = value
            self._database.write_to_file()  # as the entry's data was changed, write database to disk (again)
            return old

        except KeyError as ex:
            Log.error(f"Invalid key for database entry type {self._type_name}: {key}", ex)

    def __str__(self):
        return str(self._data)

    def get_data_copy(self, filter_keys: bool = True) -> dict:
        data = self._data.copy()

        if filter_keys and self.get_filter_keys():
            for key in self.get_filter_keys():
                data[key] = "<filtered>"

        return data

    @abstractmethod
    def get_filter_keys(self) -> List[str]:
        pass

    def matches_kwargs(self, **kwargs) -> bool:
        for k, v in kwargs.items():
            if self[k] != v:
                return False

        Log.trace(f"{repr(self)} matched with kwargs")
        return True


# Database classes

class Accounts(AbstractDatabase):
    def __init__(self):
        super().__init__("accounts.json")

    def get_entries_as_json(self) -> list:
        return_list = []

        for entry in self.get_entries():
            entry.get_data_copy(filter_keys=False)

        return return_list

    def load_entries_from_json(self, entries_as_json) -> set:
        pass

    def create_random_account(self):  # todo implement
        raise NotImplementedError


class Songs(AbstractDatabase):
    def __init__(self):
        super().__init__("songs.json")

    def get_entries_as_json(self) -> Union[dict, list]:
        pass

    def load_entries_from_json(self, entries_as_json) -> set:
        pass

    def get_song_by_id(self, song_id: str):
        self.find_single(song_id=song_id)

    def get_song_count(self) -> int:
        return len(self._entries)


# Database entry classes

class Song(AbstractDatabaseEntry):
    def __init__(self, database, **kwargs):
        super().__init__(database, {
            "convert_time": 0,
            "dislikes": set(),
            "download_time": 0,
            "duration": 0,
            "likes": set(),
            "name": None,
            "platform": None,
            "plays": 0,
            "song_id": None,
        }, **kwargs)

    def __repr__(self):
        return f"<Song {self['song_id']}, name={self['name']}>"

    def get_filter_keys(self) -> List[str]:
        pass  # all data of a song is public

    def copy_to_frontend_if_absent(self):
        """Copy the song file to frontend cache if it is absent"""

        backend_file = f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}/{self['song_id']}.mp3"
        frontend_file = f"{CWD_PATH}/{FRONTEND_AUDIO_CACHE}/{self['song_id']}.mp3"

        if os.path.exists(frontend_file):
            Log.trace("Frontend cache already has song file")
        else:
            Log.trace("Copying song file from backend to frontend")
            shutil.copyfile(backend_file, frontend_file)

    def dislike(self, username):
        self["dislikes"].add(username)

    def get_url(self):
        return f"audio/{self['song_id']}.mp3"

    def increment_plays(self, amount=1):
        self["plays"] += amount

    def like(self, username):
        self["likes"].add(username)

    def undislike(self, username):
        try:
            self["dislikes"].remove(username)
        except KeyError as ex:
            Log.error(f"User with username {username} didn't dislike this song", ex)

    def unlike(self, username):
        try:
            self["likes"].remove(username)
        except KeyError as ex:
            Log.error(f"User with username {username} didn't like this song", ex)


class Account(AbstractDatabaseEntry):
    def __init__(self, database, **kwargs):
        super().__init__(database, {
            "username": None,
            "password": None,
            "money": 0
        }, **kwargs)

    def __repr__(self):
        return f"<Account {self['name']}, money={self['money']}>"

    def get_filter_keys(self) -> List[str]:
        return ["password"]

