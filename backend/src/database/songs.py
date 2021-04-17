from convenience import *
from .abstract_database import AbstractDatabase
from .song import Song


class Songs(AbstractDatabase):
    def __init__(self, shove):
        super().__init__(Song, "songs.json")
        self.shove = shove
        self.current_song = None
        # self.current_song_duration: int = 0  # todo implement sending user current song and progress of the song (live radio-like)
        self.current_song_time_left: int = 0
        self.current_song_requested_by = None
        self.queue = Queue()
        self.shuffle_queue = False
        eventlet.spawn(song_end_watcher_task, self)

    def broadcast_rating_of(self, song):
        """Broadcast a song's rating to all users, and whether they liked/disliked"""

        for user in self.shove.get_all_users():
            self.shove.send_packet_to(user, "song_rating", song.get_rating_of(user))

    def get_random(self) -> Song:
        entries = self.get_entries()
        if entries:
            return random.choice(list(entries))

    def get_random_popular(self) -> Song:
        # todo prevent playing same song twice in a row
        # # if a song has a good enough likes/(likes+dislikes)) ratio, it is "popular"
        entries = self.get_entries()
        if entries:
            eligible = [song for song in entries if song.is_popular()]

            return random.choice(eligible)

    def play(self, song, requested_by):
        Log.info(f"Playing song {song}")
        song.increment_plays(self.shove.get_user_count())
        self.current_song = song
        self.current_song_time_left = int(song["duration"])
        self.current_song_requested_by = requested_by

        self.shove.send_packet_to_everyone("play_song", {
            "author": self.current_song_requested_by.get_username() if self.current_song_requested_by else None,
            "name": song["name"],
            "plays": song["plays"],
            "song_bytes": open(f"{FILES_FOLDER}/{SONGS_FOLDER}/{song['song_id']}.mp3", "rb").read()
        })

        self.broadcast_rating_of(song)

    def skip(self):
        Log.trace("Skipping the current song")

        if not self.current_song:
            Log.trace("No song is playing, ignoring skip call")
            return

        self.current_song = None
        self.current_song_time_left = 0
        self.current_song_requested_by = None

    def toggle_shuffle_queue(self):  # todo implement
        self.shuffle_queue = not self.shuffle_queue
        Log.trace(f"Set shuffle queue to: {self.shuffle_queue}")


def song_end_watcher_task(database: Songs):
    set_greenlet_name("SongEndWatcher")

    database_is_empty = not database.get_entries()

    while True:
        if database.current_song_time_left > 0:
            time.sleep(1)
            database.current_song_time_left -= 1

        elif database.shove.get_all_users():
            Log.trace("Song ended and user(s) online, starting new song")

            try:
                song, requested_by = database.queue.get(block=database_is_empty)  # get next song in queue, if there is one
                database_is_empty = False  # next time, dont block (if it was blocking)
                Log.trace(f"Got {song} from queue")

            except Empty:
                song, requested_by = database.get_random_popular(), None  # otherwise get a random popular song
                Log.trace(f"Queue is empty, got random popular song {song}")

            database.play(song, requested_by)

        else:
            time.sleep(1)  # idle untill new user connects
