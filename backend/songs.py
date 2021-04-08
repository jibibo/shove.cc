from convenience import *

from abstract_database import AbstractDatabase, AbstractDatabaseEntry


class Songs(AbstractDatabase):
    def __init__(self):
        super().__init__("songs.json")

    def get_entries_as_json(self) -> list:
        entries_as_json = []

        for entry in self.get_entries():
            entry_as_json = entry.get_data_copy()
            for k in ["dislikes", "likes"]:  # convert these data types from set to list
                entry_as_json[k] = list(entry_as_json[k])

            entries_as_json.append(entry_as_json)

        return entries_as_json

    def get_entries_from_json(self, entries_as_json) -> set:
        entries = set()

        for entry_as_json in entries_as_json:
            entry = Song(self, **entry_as_json)
            for k in ["dislikes", "likes"]:  # convert these data types from list to set
                entry[k] = set(entry[k])

            entries.add(entry)

        return entries

    def get_song_by_id(self, song_id: str):
        self.find_single(song_id=song_id)

    def get_song_count(self) -> int:
        return len(self._entries)


class Song(AbstractDatabaseEntry):
    def __init__(self, database, **kwargs):
        super().__init__(database, {
            "convert_time": 0,
            "dislikes": set(),
            "download_time": 0,
            "duration": 0,
            "likes": set(),
            "name": None,
            "platform": None,
            "plays": 0,
            "song_id": None,
        }, **kwargs)

    def __repr__(self):
        return f"<Song {self['song_id']}, name: {self['name']}>"

    def get_filter_keys(self) -> List[str]:
        pass  # all data of a song is public

    def copy_to_frontend_if_absent(self):
        """Copy the song file to frontend cache if it is absent"""

        backend_file = f"{CWD_PATH}/{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}/{self['song_id']}.mp3"
        frontend_file = f"{CWD_PATH}/{FRONTEND_CACHE_FOLDER}/{SONGS_FOLDER}/{self['song_id']}.mp3"

        if os.path.exists(frontend_file):
            Log.trace("Frontend cache already has song file")
        else:
            Log.trace("Copying song file from backend to frontend")
            shutil.copyfile(backend_file, frontend_file)

    def get_dislike_count(self) -> int:
        return len(self["dislikes"])

    def get_like_count(self) -> int:
        return len(self["likes"])

    def get_rating_of(self, username) -> dict:
        return {
            "disliked": username in self["dislikes"] if username else False,
            "liked": username in self["likes"] if username else False
        }

    def get_url(self):
        return f"cache/songs/{self['song_id']}.mp3"

    def increment_plays(self, amount=1):
        self["plays"] += amount  # triggers db write

    def play(self, shove, author):
        Log.trace(f"Playing {self}")
        self.copy_to_frontend_if_absent()
        self.increment_plays(shove.get_user_count())
        shove.latest_song = self
        shove.latest_song_author = author

        self.send_rating_packet(shove)

        shove.send_packet_to_everyone("play_song", {
            "author": shove.latest_song_author.get_username(),
            "url": self.get_url(),
            "name": self["name"],
            "plays": self["plays"],
        })

    def send_rating_packet(self, shove):
        """Send a packet containing the current song's ratings.
        Called when the rating has been updated or a new song started playing."""

        dislike_count = self.get_dislike_count()
        like_count = self.get_like_count()

        for user in shove.get_all_users():
            shove.send_packet_to(user, "song_rating", {
                "dislikes": dislike_count,
                "likes": like_count,
                "you": self.get_rating_of(user.get_username())
            })

    def toggle_dislike(self, username) -> bool:
        if username in self["dislikes"]:  # if user disliked, remove the dislike
            self["dislikes"].remove(username)
            return False

        if username in self["likes"]:  # else if user wants to dislike, so remove their like
            self["likes"].remove(username)

        self["dislikes"].add(username)
        return True

    def toggle_like(self, username) -> bool:
        if username in self["likes"]:  # if user liked, remove them
            self["likes"].remove(username)
            return False

        if username in self["dislikes"]:  # else if user wants to like, remove their dislike
            self["dislikes"].remove(username)

        self["likes"].add(username)
        return True