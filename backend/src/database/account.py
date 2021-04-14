from convenience import *

from .abstract_database_entry import AbstractDatabaseEntry


class Account(AbstractDatabaseEntry):
    """An instance containing a users' data, assigned if they log in"""

    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)

    def __repr__(self):
        return f"<Account #{self['entry_id']}, username: {self['username']}>"

    @staticmethod
    def convert_parsed_json_data(parsed_json: dict) -> dict:
        return parsed_json  # no need to change anything; all types are json serializable

    @staticmethod
    def get_default_data() -> dict:
        return {
            "avatar_filename": str(),
            "avatar_type": str(),
            "money": int(),
            "password": str(),
            "username": str(),
        }

    @staticmethod
    def get_filter_keys() -> List[str]:
        return [
            "password",
            "avatar_filename"
        ]

    def get_jsonable(self, filter_data=True) -> dict:
        data_copy = self.get_data_copy(filter_data=filter_data)

        return data_copy

    def get_avatar_bytes(self) -> bytes:
        if self["avatar_filename"]:
            try:
                with open(f"{FILES_FOLDER}/{AVATARS_FOLDER}/{self['avatar_filename']}", "rb") as f:
                    return f.read()
            except FileNotFoundError:
                Log.warning(f"Could not find avatar file {self['avatar_filename']}")
