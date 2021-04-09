from convenience import *


class AbstractDatabase(ABC):
    def __init__(self, filename: str):
        """Abstract class for database instance that contains entries, to be saved in a json file"""

        self._filename: str = filename
        self._file_abs: str = f"{CWD_PATH}/{BACKEND_DATA_FOLDER}/{filename}"
        self._last_entry_id: int = 0
        self._entries: Set[AbstractDatabaseEntry] = set()
        self._type_name = type(self).__name__

        Log.trace(f"Creating DB from file: {self}")

        self.has_read_from_file: bool = False
        self.read_from_file()

        Log.trace(f"Created DB: {self}")

    def __repr__(self):
        return f"<DB '{self._type_name}', entries: {self.get_entries_count()}>"

    def add_entry(self, entry):
        self._entries.add(entry)

    @abstractmethod
    def get_entries_as_json_list(self) -> list:
        pass

    @abstractmethod
    def get_entries_from_json_list(self, entries_as_json_list: list) -> set:
        pass

    def find_multiple(self, raise_if_missing: bool = True, **kwargs) -> set:
        Log.trace(f"Finding DB entries w/ kwargs: {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        candidates = set()
        for entry in self._entries:
            if entry.matches_kwargs(**kwargs):
                candidates.add(entry)

        if candidates:
            return candidates
        elif raise_if_missing:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No DB entries found")

    def find_single(self, raise_if_missing: bool = True, **kwargs):
        Log.trace(f"Finding DB entry w/ kwargs: {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        for entry in self._entries:
            if entry.matches_kwargs(**kwargs):
                return entry

        if raise_if_missing:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No DB entry found")

    def get_entries(self) -> set:
        return self._entries

    def get_entries_count(self) -> int:
        return len(self._entries)

    def get_entries_data_sorted(self, key, reverse=False) -> list:
        return [entry.get_data_copy() for entry in sorted(self._entries, key=key, reverse=reverse)]

    def get_entries_sorted(self, key, reverse=False) -> list:  # unused?
        return sorted(self._entries, key=key, reverse=reverse)

    def get_next_entry_id(self) -> int:
        self._last_entry_id += 1
        Log.trace(f"Got next DB entry ID: {self._last_entry_id}")
        return self._last_entry_id

    def read_from_file(self):
        """Read and loa7d the DB's entries from file.
        Called once upon DB creation."""

        if self.has_read_from_file:
            Log.warn("Already read from DB file! Ignoring read_from_file call")
            return

        with open(self._file_abs, "r") as f:
            data = json.load(f)

        try:
            self._last_entry_id = data["last_entry_id"]
        except KeyError:  # database is empty, use default value (already 0)
            pass

        try:
            entries_as_json_list = data["entries"]
        except KeyError:  # database is empty, use default value (empty set)
            pass
        else:
            self._entries = self.get_entries_from_json_list(entries_as_json_list)

        self.has_read_from_file = True
        Log.debug(f"{self} read from file")

    def remove_entry(self, entry):
        self._entries.remove(entry)

    def write_to_file(self):  # todo write to temp file while writing to prevent potential data loss during crashes (if needed?)
        """Write the DB's entries to disk, taking into account non-JSON variable types.
        Called when creating new DB entries or modifying existing ones."""

        # Log.trace(f"{self} writing to DB file")

        # sort by entry id in the database
        entries_as_json_list_sorted = sorted(self.get_entries_as_json_list(), key=lambda e: e["entry_id"])

        with open(self._file_abs, "w") as f:
            json.dump({
                "last_entry_id": self._last_entry_id,
                "entries": entries_as_json_list_sorted
            }, f, indent=2)

        # Log.trace(f"{self} wrote to DB file")


class AbstractDatabaseEntry(ABC):
    def __init__(self, database: AbstractDatabase, default_data: dict, **kwargs):
        """Creates a new DB entry for specific database.
        default_data contains dict of default key-values, keys absent in this dict raise a ValueError.
        **kwargs contains overriding key-values."""

        self._type_name = type(self).__name__
        self._database: AbstractDatabase = database

        assert "entry_id" not in default_data, "Key 'entry_id' not allowed in default_data!"
        self._data = default_data

        if "entry_id" not in kwargs:
            # initialized during runtime (not on startup file read), create new entry id
            # if not initialized during runtime, kwargs should NEVER contain entry_id!
            self._data.update(entry_id=database.get_next_entry_id())

        for key in kwargs:
            if key not in default_data and key != "entry_id":
                raise ValueError(f"Invalid key '{key}' for: {self}")

        self._data.update(kwargs)

        self._database.add_entry(self)
        self.trigger_db_write()  # write to file as new entry has been added

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

    def delete(self):
        Log.trace(f"Deleting DB entry {self}")
        self._database.remove_entry(self)
        self.trigger_db_write()  # update DB as an entry has been removed
        Log.trace(f"Deleted DB entry {self}")

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
