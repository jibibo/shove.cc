from convenience import *

from .abstract_database import AbstractDatabase
from .account import Account


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
                username = "".join(random.choices(USERNAME_VALID_CHARACTERS, k=USERNAME_MAX_LENGTH)).lower()
                if self.find_single(raise_if_missing=False, username=username):  # username exists (chance of 1 in >1e24)
                    username_attempts += 1
                    if username_attempts == max_attempts:
                        raise RuntimeError(f"Could not create a unique username in {max_attempts} attempts")

                else:
                    break

        money = random.randint(RANDOM_MONEY_MIN, RANDOM_MONEY_MAX)
        account = self.create_entry(username=username, money=money)

        return account

