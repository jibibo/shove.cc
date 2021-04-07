from convenience import *


class Song:
    def __init__(self, platform, song_id, name, duration, download_time, convert_time):
        self.platform = platform,
        self.song_id = song_id
        self.name = name
        self.duration = duration
        self.download_time = download_time
        self.convert_time = convert_time
        self.url = f"audio/{song_id}.mp3"
        self.plays = 0
        self.likes: Set[str] = set()  # list of usernames that liked/disliked this song
        self.dislikes: Set[str] = set()
        Log.trace(f"Created Song object for {platform} {song_id}: '{name}', duration={duration}, download_time={download_time}, convert_time={convert_time}")

    def __repr__(self):
        return f"<Song {self.song_id}: {self.name}, plays: {self.plays}>"

    def like(self, username):
        self.likes.add(username)

    def unlike(self, username):
        try:
            self.likes.remove(username)
        except KeyError:
            Log.warn(f"User with username {username} didn't like this song")

    def dislike(self, username):
        self.dislikes.add(username)

    def undislike(self, username):
        try:
            self.dislikes.remove(username)
        except KeyError:
            Log.warn(f"User with username {username} didn't dislike this song")

    def increment_plays(self, amount=1):
        self.plays += amount
