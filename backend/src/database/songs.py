from .abstract_database import AbstractDatabase
from .song import Song


class Songs(AbstractDatabase):
    def __init__(self):
        super().__init__(Song, "songs.json")
