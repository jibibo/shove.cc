from convenience import *


class Account:
    def __init__(self, **k_v):
        self.data: dict = {
            "username": None,
            "password": None,
            "money": 0
        }

        for k, v in k_v.items():
            if k not in self.data.keys():
                raise ValueError(f"Invalid account key: {k} = {v}")

        self.data.update(k_v)

    def __getitem__(self, key):
        try:
            return self.data[key]

        except KeyError as ex:
            Log.error(f"No such key in account data: {key}", ex)

    def __repr__(self):
        return f"<Account of '{self['username']}', {self}>"

    def __setitem__(self, key, value):
        try:
            old = self.data[key]
            self.data[key] = value
            return old

        except KeyError as ex:
            Log.error(f"No such key in account data: {key}", ex)

    def __str__(self):
        return str(self.data)
