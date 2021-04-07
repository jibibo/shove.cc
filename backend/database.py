from convenience import *


# Astract classes

class AbstractDatabase(ABC):
    def __init__(self, filename):
        self._filename = filename
        self._file_abs = f"{CWD_PATH}/{DATABASES_DIRECTORY}/{filename}"
        self._entries = set()

        self.read_from_file()

        Log.trace(f"Created DB for filename: {filename}")

    def add_entry(self, entry):
        self._entries.add(entry)

    def find_multiple(self, raise_not_found: bool = True, **kwargs) -> set:
        Log.trace(f"Finding DB entries w/ kwargs: {kwargs}")

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
            Log.trace(f"No DB entries found")

    def find_single(self, raise_not_found: bool = True, **kwargs):
        Log.trace(f"Finding DB entry w/ kwargs: {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        for entry in self._entries:
            if entry.matches_kwargs(**kwargs):
                return entry

        if raise_not_found:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No DB entry found")

    def get_entries(self) -> set:
        return self._entries

    @abstractmethod
    def get_entries_as_json(self) -> list:
        pass

    @abstractmethod
    def get_entries_from_json(self, entries_as_json) -> set:
        pass

    def get_sorted(self, key, reverse=False) -> list:
        return sorted(self._entries, key=key, reverse=reverse)

    def read_from_file(self) -> set:
        """Read and load the DB's entries from file. Called once upon DB creation."""

        with open(self._file_abs, "r") as f:
            entries_as_json = json.load(f)

        entries = self.get_entries_from_json(entries_as_json)
        return entries

    def write_to_file(self):  # todo write to temp file while writing to prevent potential data loss during crashes (if needed?)
        """Write the DB's entries to disk, taking into account non-JSON variable types.
        Called when creating new DB entries or modifying existing ones."""

        # Log.trace(f"Writing to database file {self._filename}")

        data_as_json = self.get_entries_as_json()
        with open(self._file_abs, "w") as f:
            json.dump(data_as_json, f, indent=2)


class AbstractDatabaseEntry(ABC):
    def __init__(self, database, default_data: dict, **kwargs):
        self._type_name = type(self).__name__
        self._data = default_data

        for key in kwargs:
            if key not in default_data:
                raise ValueError(f"Invalid key '{key}' for: {self}")

        self._data.update(kwargs)

        self._database = database
        database.add_entry(self)
        self.trigger_db_write()  # write db to file if new database entry gets created

        Log.trace(f"Created DB entry: {self}")

    def __getitem__(self, key):
        try:
            return self._data[key]

        except KeyError as ex:
            Log.error(f"Invalid key '{key}' for: {self}", ex)

    def __setitem__(self, key, value):
        try:
            old = self._data[key]
            self._data[key] = value
            self.trigger_db_write()  # as the entry's data was changed, write database to disk
            return old

        except KeyError as ex:
            Log.error(f"Invalid key '{key}' for: {self}", ex)

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

        Log.trace(f"{self} matched with kwargs")
        return True

    def trigger_db_write(self):
        """Trigger the DB this entry is attached to to write the DB entries to disk.
        Required to call if variables are modified indirectly (e.g. list appends/removes)"""
        self._database.write_to_file()


# Database classes

class Accounts(AbstractDatabase):
    def __init__(self):
        super().__init__("accounts.json")

    def get_entries_as_json(self) -> list:
        entries_as_json = []

        for entry in self.get_entries():
            entry_as_json = entry.get_data_copy(filter_keys=False)
            entries_as_json.append(entry_as_json)  # no unsupported types in Account objects

        return entries_as_json

    def get_entries_from_json(self, entries_as_json) -> set:
        entries = set()

        for entry_as_json in entries_as_json:
            entries.add(Account(self, **entry_as_json))

        return entries

    def create_random_account(self):  # todo implement
        raise NotImplementedError


class Songs(AbstractDatabase):
    def __init__(self):
        super().__init__("songs.json")

    def get_entries_as_json(self) -> list:
        entries_as_json = []

        for entry in self.get_entries():
            entry_as_json = entry.get_data_copy()
            for k in ["dislikes", "likes"]:  # convert these data types from set to list
                entry_as_json[k] = list(entry_as_json[k])

            entries_as_json.append(entry_as_json)

        return entries_as_json

    def get_entries_from_json(self, entries_as_json) -> set:
        entries = set()

        for entry_as_json in entries_as_json:
            entry = Song(self, **entry_as_json)
            for k in ["dislikes", "likes"]:  # convert these data types from list to set
                entry[k] = set(entry[k])

            entries.add(entry)

        return entries

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

    def get_dislike_count(self) -> int:
        return len(self["dislikes"])

    def get_like_count(self) -> int:
        return len(self["likes"])

    def get_rating_of(self, username) -> dict:
        return {
            "disliked": username in self["dislikes"] if username else False,
            "liked": username in self["likes"] if username else False
        }

    def get_url(self):
        return f"audio/{self['song_id']}.mp3"

    def increment_plays(self, amount=1):
        self["plays"] += amount  # triggers db write

    def play(self, shove, author):
        Log.trace(f"Playing {self}")
        self.copy_to_frontend_if_absent()
        self.increment_plays(shove.get_user_count())
        shove.latest_song = self
        shove.latest_song_author = author

        self.send_rating_packet(shove)

        shove.send_packet_to_everyone("play_song", {
            "author": shove.latest_song_author.get_username(),
            "url": self.get_url(),
            "name": self["name"],
            "plays": self["plays"],
        })

    def send_rating_packet(self, shove):
        """Send a packet containing the current song's ratings.
        Called when the rating has been updated or a new song started playing."""

        dislike_count = self.get_dislike_count()
        like_count = self.get_like_count()

        for user in shove.get_all_users():
            shove.send_packet_to(user, "song_rating", {
                "dislikes": dislike_count,
                "likes": like_count,
                "you": self.get_rating_of(user.get_username())
            })

    def toggle_dislike(self, username) -> bool:
        if username in self["dislikes"]:  # if user disliked, remove the dislike
            self["dislikes"].remove(username)
            return False

        if username in self["likes"]:  # else if user wants to dislike, so remove their like
            self["likes"].remove(username)

        self["dislikes"].add(username)
        return True

    def toggle_like(self, username) -> bool:
        if username in self["likes"]:  # if user liked, remove them
            self["likes"].remove(username)
            return False

        if username in self["dislikes"]:  # else if user wants to like, remove their dislike
            self["dislikes"].remove(username)

        self["likes"].add(username)
        return True


class Account(AbstractDatabaseEntry):
    def __init__(self, database, **kwargs):
        super().__init__(database, {
            "username": None,
            "password": None,
            "money": 0
        }, **kwargs)

    def __repr__(self):
        return f"<Account {self['username']}, money={self['money']}>"

    def get_filter_keys(self) -> List[str]:
        return ["password"]

