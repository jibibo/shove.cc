from convenience import *


class Account:
    def __init__(self, **k_v):
        self._data: dict = {
            "username": None,
            "password": None,
            "money": 0
        }

        for k, v in k_v.items():
            if k not in self._data.keys():
                raise ValueError(f"Invalid account key: {k} = {v}")

        self._data.update(k_v)

    def __getitem__(self, key):
        try:
            return self._data[key]

        except KeyError as ex:
            Log.error(f"No such key in account data: {key}", ex)

    def __repr__(self):
        return f"<Account of '{self['username']}', {self}>"

    def __setitem__(self, key, value):
        try:
            old = self._data[key]
            self._data[key] = value
            return old

        except KeyError as ex:
            Log.error(f"No such key in account data: {key}", ex)

    def __str__(self):
        return str(self._data)

    def get_data(self, filter_sensitive=True) -> dict:
        copy = self._data.copy()

        if filter_sensitive:
            for key in ["password"]:
                copy[key] = "*"

        return copy
