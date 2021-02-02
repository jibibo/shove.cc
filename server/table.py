from util_server import *


class Table:
    def __init__(self, server, name, min_players=2, max_players=10):
        self.server = server
        self.name = name
        self.min_players = min_players
        self.max_players = max_players

    def __repr__(self):
        return f"Table {self.name}"
