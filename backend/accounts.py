from convenience import *

from abstract_database import AbstractDatabase, AbstractDatabaseEntry


class Accounts(AbstractDatabase):
    def __init__(self):
        super().__init__("accounts.json")

    def get_entries_as_json_list(self) -> list:
        entries_as_json = []

        for entry in self.get_entries():
            entry_as_json = entry.get_data_copy(filter_keys=False)
            entries_as_json.append(entry_as_json)  # no unsupported types in Account objects

        return entries_as_json

    def get_entries_from_json_list(self, entries_as_json_list: list) -> set:
        entries = set()

        for entry_as_json in entries_as_json_list:
            entries.add(Account(self, **entry_as_json))

        return entries

    def create_random_account(self, preferred_username=None):
        """Creates a random Account (with optional name) instance and returns it"""

        Log.trace("Creating random account")

        username = None
        if preferred_username:
            if self.find_single(raise_if_missing=False, username=preferred_username):
                username = None
            else:
                username = preferred_username  # username is not taken, so we good

        if not username:
            username_attempts = 0
            max_attempts = 1
            while username_attempts < max_attempts:  # prevent hardcoding "while True" for infinite loops
                username = "".join(random.choices(USERNAME_VALID_CHARACTERS, k=USERNAME_MAX_LENGTH))
                if self.find_single(raise_if_missing=False, username=username):  # username exists (chance of 1 in >1e24)
                    username_attempts += 1
                    if username_attempts == max_attempts:
                        raise RuntimeError(f"Could not create a unique username in {max_attempts} attempts")

                else:
                    break

        money = random.randint(RANDOM_MONEY_MIN, RANDOM_MONEY_MAX)
        account = Account(self, username=username, money=money)

        return account


class Account(AbstractDatabaseEntry):
    def __init__(self, database: AbstractDatabase, **kwargs):
        super().__init__(database, {
            "username": None,
            "password": None,
            "money": 0
        }, **kwargs)

    def __repr__(self):
        return f"<Account {self['entry_id']}, money: {self['money']}>"

    def get_filter_keys(self) -> List[str]:
        return ["password"]
