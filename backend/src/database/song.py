from convenience import *

from .abstract_database_entry import AbstractDatabaseEntry


class Song(AbstractDatabaseEntry):
    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)

    def __repr__(self):
        return f"<Song #{self['entry_id']}, name: {self['name']}>"

    @staticmethod
    def convert_parsed_json_data(json_data: dict) -> dict:
        for k in ["dislikes", "likes"]:  # convert these data types from list to set
            json_data[k] = set(json_data[k])

        return json_data

    @staticmethod
    def get_default_data() -> dict:
        return {
            "convert_time": 0,
            "dislikes": set(),
            "download_time": 0,
            "duration": 0,
            "likes": set(),
            "name": None,
            "platform": None,
            "plays": 0,
            "song_id": None,
        }

    @staticmethod
    def get_filter_keys() -> List[str]:
        pass  # nothing to filter, all data of a song is public

    def get_jsonable(self, filter_data=True) -> dict:
        data_copy = self.get_data_copy(filter_data=filter_data)

        for k in ["dislikes", "likes"]:  # convert these data types from set to list
            data_copy[k] = list(data_copy[k])

        return data_copy

    def get_dislike_count(self) -> int:
        return len(self["dislikes"])

    def get_like_count(self) -> int:
        return len(self["likes"])

    def get_like_ratio(self) -> float:
        likes = self.get_like_count()
        dislikes = self.get_dislike_count()
        total = likes + dislikes

        try:
            return likes / total
        except ZeroDivisionError:  # if there are no likes or dislikes, it is considered 0.5
            return 0.5

    def get_rating_of(self, user) -> dict:
        """The packet containing the current song's ratings,
        unique for each user as they might have liked/disliked the song"""

        dislike_count = self.get_dislike_count()
        like_count = self.get_like_count()

        return {
            "dislikes": dislike_count,
            "likes": like_count,
            "you": {
                "disliked": user.get_username() in self["dislikes"] if user and user.is_logged_in() else False,
                "liked": user.get_username() in self["likes"] if user and user.is_logged_in() else False
            }
        }

    def increment_plays(self, amount=1):
        self["plays"] += amount  # triggers db write as it assigns with "="

    def is_popular(self) -> bool:
        return self.get_like_ratio() >= POPULAR_SONGS_RATIO_MIN

    def toggle_dislike(self, username):
        if username in self["likes"]:  # remove the user's like in any case
            self["likes"].remove(username)

        if username in self["dislikes"]:  # if user disliked, remove the dislike
            self["dislikes"].remove(username)
        else:
            self["dislikes"].add(username)

        self.trigger_db_write()

    def toggle_like(self, username):  # todo toggle_like and toggle_dislike are not DRY
        if username in self["dislikes"]:  # remove the user's dislike in any case
            self["dislikes"].remove(username)

        if username in self["likes"]:  # if user liked, remove the like
            self["likes"].remove(username)
        else:
            self["likes"].add(username)

        self.trigger_db_write()
