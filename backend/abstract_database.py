from convenience import *


class AbstractDatabase(ABC):  # todo implement unique id's, tracked in the json.file, so db becomes a dict with {next_id: int, entries: []}
    def __init__(self, filename: str):
        """Abstract class for database instance that contains entries, to be saved in a json file"""

        self._filename = filename
        self._file_abs = f"{CWD_PATH}/{BACKEND_DATA_FOLDER}/{filename}"
        self._entries: Set[AbstractDatabaseEntry] = set()
        self._type_name = type(self).__name__

        Log.trace(f"Creating DB from file: {self}")

        self.read_from_file()

        Log.trace(f"Created DB: {self}")

    def __repr__(self):
        return f"<DB '{self._type_name}', entries: {self.get_entries_count()}>"

    @abstractmethod
    def get_entries_as_json(self) -> list:
        pass

    @abstractmethod
    def get_entries_from_json(self, entries_as_json: list) -> set:
        pass

    def add_entry(self, entry):
        Log.trace(f"Adding entry {entry} to {self}")
        self._entries.add(entry)
        self.write_to_file()  # write to file as new entry has been added

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

    def read_from_file(self):
        """Read and load the DB's entries from file. Called once upon DB creation."""

        with open(self._file_abs, "r") as f:
            entries_as_json = json.load(f)

        self._entries = self.get_entries_from_json(entries_as_json)

    def remove_entry(self, entry):
        Log.trace(f"Removing entry {entry} from {self}")
        self._entries.remove(entry)
        self.write_to_file()  # update as an entry has been removed

    def write_to_file(self):  # todo write to temp file while writing to prevent potential data loss during crashes (if needed?)
        """Write the DB's entries to disk, taking into account non-JSON variable types.
        Called when creating new DB entries or modifying existing ones."""

        # Log.trace(f"Writing to database file {self._filename}")

        data_as_json = self.get_entries_as_json()
        with open(self._file_abs, "w") as f:
            json.dump(data_as_json, f, indent=2)


class AbstractDatabaseEntry(ABC):
    def __init__(self, database: AbstractDatabase, default_data: dict, **kwargs):
        self._type_name = type(self).__name__
        self._data = default_data

        for key in kwargs:
            if key not in default_data:
                raise ValueError(f"Invalid key '{key}' for: {self}")

        self._data.update(kwargs)

        self._database: AbstractDatabase = database
        database.add_entry(self)

        Log.trace(f"Created DB entry: {self}")

    def __del__(self):
        self._database.remove_entry(self)

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
