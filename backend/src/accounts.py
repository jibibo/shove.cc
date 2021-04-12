from convenience import *

from abstract_database import AbstractDatabase, AbstractDatabaseEntry


class Accounts(AbstractDatabase):
    def __init__(self):
        super().__init__(Account, "accounts.json")

    def create_random_account(self, username=None):
        """Creates a random Account (with optional chosen name) instance and returns it"""

        Log.trace("Creating random account")

        if username:
            if self.find_single(raise_if_missing=False, username=username):
                raise ValueError("Username is taken")

        else:
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
        account = self.create_entry(username=username, money=money)

        return account


class Account(AbstractDatabaseEntry):
    """An instance containing a users' data, assigned if they log in"""

    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)

    def __repr__(self):
        return f"<Account #{self['entry_id']}, username: {self['username']}>"

    @staticmethod
    def convert_parsed_json_data(parsed_json: dict) -> dict:
        return parsed_json  # no need to change anything

    @staticmethod
    def get_default_data() -> dict:
        return {
            "username": None,
            "password": None,
            "money": 0
        }

    @staticmethod
    def get_filter_keys() -> List[str]:
        return [
            "password"
        ]

    def get_jsonable(self, filter_data=True) -> dict:
        return self.get_data_copy(filter_data)
