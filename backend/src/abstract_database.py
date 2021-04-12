from convenience import *


class AbstractDatabase(ABC):
    def __init__(self, entry_class, filename: str):
        """Abstract class for database instance that contains entries, to be saved in a json file"""

        self._entry_class = entry_class
        self._filename: str = filename
        self._file_path: str = f"{DATABASES_FOLDER}/{filename}"
        self._last_entry_id: int = 0
        self._entries: Set[AbstractDatabaseEntry] = set()

        Log.trace(f"Creating DB from file: {self}")

        self._has_read_from_file: bool = False
        self._read_from_disk()

        Log.trace(f"Created DB: {self}")

    def __repr__(self):
        return f"<DB '{type(self).__name__}', entries: {self.get_entries_count()}>"

    def _get_next_entry_id(self) -> int:
        self._last_entry_id += 1
        Log.trace(f"Got next DB entry ID: {self._last_entry_id}")
        return self._last_entry_id

    def _read_from_disk(self):
        """Read and load the DB's entries from disk.
        Called ONCE: on DB creation."""

        if self._has_read_from_file:
            Log.warn(f"{self} already read from disk! Ignoring call")
            return

        with open(self._file_path, "r") as f:
            data = json.load(f)

        try:
            self._last_entry_id = data["last_entry_id"]
        except KeyError:
            pass  # database is empty, keep last_entry_id 0

        try:
            entries_as_json_list = data["entries"]
        except KeyError:
            pass  # database is empty, keep entries as an empty set
        else:
            # database on disk is not empty, create DB entries
            for entry_as_json_dict in entries_as_json_list:
                self.create_entry(read_from_file=True, **entry_as_json_dict)

        self._has_read_from_file = True
        Log.debug(f"{self} read from file")

    def create_entry(self, read_from_file=False, **kwargs):
        """Creates a new DB entry for this database.
        default_data contains dict of default key-values.
        kwargs keys absent in this dict raise a ValueError.
        kwargs contains overriding key-values.
        Returns the newly created DB entry instance."""

        if read_from_file:
            # entry created because DB read from file, so convert JSON-serializable
            # objects to their proper counterpart if required
            kwargs = self._entry_class.convert_parsed_json_data(kwargs)

        if "entry_id" in kwargs:
            if not read_from_file:
                raise ValueError("Key 'entry_id' not allowed in kwargs if not reading from file")
        else:
            # if entry_id not set in kwargs, assign a new one
            kwargs["entry_id"] = self._get_next_entry_id()

        new_entry = self._entry_class(self, **kwargs)

        self._entries.add(new_entry)

        if not read_from_file:
            # entry created during runtime, so new data that has to be saved to file
            self.write_to_disk()

        return new_entry

    def find_multiple(self, raise_if_missing=True, match_casing=False, **kwargs) -> set:
        Log.trace(f"Finding DB entries w/ kwargs (match casing: {match_casing}): {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        candidates = set()
        for entry in self._entries:
            if entry.matches_kwargs(match_casing, **kwargs):
                candidates.add(entry)

        if candidates:
            return candidates
        elif raise_if_missing:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No DB entries found")
            return set()

    def find_single(self, raise_if_missing=True, match_casing=False, **kwargs):
        Log.trace(f"Finding DB entry w/ kwargs (match casing: {match_casing}): {kwargs}")

        if not kwargs:
            raise ValueError("No kwargs provided")

        for entry in self._entries:
            if entry.matches_kwargs(match_casing, **kwargs):
                return entry

        if raise_if_missing:
            raise DatabaseEntryNotFound
        else:
            Log.trace(f"No DB entry found")

    def get_entries(self, key=None, reverse=False) -> set:
        """Get this DB's entries OBJECTS as-is, optional sorting with key and reverse"""

        if key:
            return set(sorted(self._entries, key=key, reverse=reverse))
        else:
            return self._entries

    def get_entries_count(self) -> int:
        return len(self._entries)

    def get_entries_jsonable(self, filter_data=True, key=None, reverse=False) -> list:
        """Get this DB's entries' data as a JSON serializable list.
        Optional key and reverse arguments for sorting."""

        if key:
            return [entry.get_jsonable(filter_data) for entry in sorted(self._entries, key=key, reverse=reverse)]
        else:
            return [entry.get_jsonable(filter_data) for entry in self._entries]

    def remove_entry(self, entry):
        Log.trace(f"Removing DB entry {self}")
        self._entries.remove(entry)
        self.write_to_disk()
        Log.trace(f"Removed DB entry {self}")

    def write_to_disk(self):
        """Write the DB's entries to disk, taking into account non-JSON variable types.
        Called when creating new DB entries or modifying existing entries."""

        # Log.trace(f"{self} writing to DB file")

        # sort by entry id in the database
        entries_json_serializable_sorted = self.get_entries_jsonable(filter_data=False, key=lambda e: e["entry_id"])

        with open(self._file_path, "w") as f:
            json.dump({
                "last_entry_id": self._last_entry_id,
                "entries": entries_json_serializable_sorted
            }, f, indent=2, sort_keys=True)

        # Log.trace(f"{self} wrote to DB file")


class AbstractDatabaseEntry(ABC):
    def __init__(self, database: AbstractDatabase, **kwargs):
        """Creates a new instance of the DB's entry type.
        Instantiate objects through the DB object, not by initializing this directly.
        If called directly, shit probably goes down, best case scenario: the new entry
        doesn't get added to the DB."""

        if not database or "entry_id" not in kwargs:
            raise ValueError("Use Database.create_entry(**kwargs), not DatabaseEntry(**kwargs)!")

        default_data = self.get_default_data()

        if "entry_id" in default_data:
            raise ValueError("Key 'entry_id' not allowed in default_data")

        for key in kwargs:
            if key not in default_data and key != "entry_id":
                raise ValueError(f"Invalid key '{key}' for: {self}")

        self._type_name = type(self).__name__
        # attach the containing DB as an easy way tell the DB to write to disk when this entry's data has been updated
        self._database: AbstractDatabase = database

        self._data = default_data
        self._data.update(kwargs)  # kwargs contains the "entry_id" key

        Log.trace(f"Created DB entry: {self}")

    def __getitem__(self, key):
        try:
            return self._data[key]

        except KeyError as ex:
            Log.error(f"Invalid key '{key}' for: {self}", ex)

    def __setitem__(self, key, value):
        try:
            self._data[key] = value

        except KeyError as ex:
            Log.error(f"Invalid key '{key}' for: {self}", ex)

        self._database.write_to_disk()  # as the entry's data was changed, write database to disk

    @staticmethod
    @abstractmethod
    def convert_parsed_json_data(json_data: dict) -> dict:
        """Convert parsed JSON data to a non-JSON data dict compatible with this DB entry type (if required).
        ONLY called ONCE after entry's data is read and parsed from disk.
        For example convert lists to sets, as those are used by this entry"""
        pass

    def get_data_copy(self, filter_data=True) -> dict:
        data = self._data.copy()

        if filter_data and self.get_filter_keys():
            for key in self.get_filter_keys():
                data[key] = "<filtered>"

        return data

    @staticmethod
    @abstractmethod
    def get_default_data() -> dict:
        """Get the default key-values of this DB entry type."""
        pass

    @staticmethod
    @abstractmethod
    def get_filter_keys() -> List[str]:
        """Get the data keys of this DB entry type require filtering before the data goes public."""
        pass

    @abstractmethod
    def get_jsonable(self, filter_data=True) -> dict:
        """Get this entry's data but JSON serializable for file writing or sending as a packet."""
        pass

    def matches_kwargs(self, match_casing=False, **kwargs) -> bool:
        if match_casing:
            for k, v in kwargs.items():
                if self[k] != v:
                    return False

        else:
            for k, v in kwargs.items():
                # only call .lower() (for ignoring casing) if checking strings
                if type(self[k]) == type(v) == str:
                    if self[k].lower() != v.lower():
                        return False
                else:
                    if self[k] != v:
                        return False

        Log.trace(f"{self} matched with kwargs")
        return True

    def trigger_db_write(self):
        """Trigger the DB this entry is attached to to write the DB entries to disk.
        Required to call if variables are modified indirectly (e.g. list appends/removes).
        If this entry's data is updated by assigning (entry[x] = y), call this is not needed."""
        self._database.write_to_disk()
