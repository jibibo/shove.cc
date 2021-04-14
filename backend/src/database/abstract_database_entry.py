from convenience import *


class AbstractDatabaseEntry(ABC):
    def __init__(self, database, **kwargs):
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
        self._database = database

        self._data = default_data
        self._data.update(kwargs)  # kwargs contains the "entry_id" key

        Log.trace(f"Created DB entry: {self}")

    def __getitem__(self, key):
        try:
            return self._data[key]

        except KeyError as ex:
            Log.error(f"Invalid key '{key}' for: {self}", ex=ex)

    def __setitem__(self, key, value):
        try:
            self._data[key] = value

        except KeyError as ex:
            Log.error(f"Invalid key '{key}' for: {self}", ex=ex)

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
