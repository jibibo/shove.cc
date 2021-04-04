from eventlet.green import subprocess  # https://stackoverflow.com/a/34649180/13216113

from convenience import *


class ProcessBroke(Exception):
    def __init__(self, value):
        self.value = str(value)

    def __str__(self):
        return self.value


class ProcessYoutubeThread(threading.Thread):
    def __init__(self, shove, youtube_id: Union[list, str]):
        super().__init__(name="ThreadYT", daemon=True)
        self.shove = shove
        if type(youtube_id) == str:
            self.youtube_ids = [youtube_id]
        elif type(youtube_id) == list:
            self.youtube_ids = youtube_id
        else:
            raise ValueError(f"Invalid youtube_id type: {type(youtube_id).__name__}")

    def run(self):
        process_youtube_wrapper(self.shove, self.youtube_ids)


def simulate_processing(seconds):
    Log.test(f"simulating for {seconds} s")
    eventlet.sleep(seconds)
    Log.test(f"Done simulating for {seconds}")


def process_youtube_wrapper(shove, youtube_ids):
    Log.trace("YT process wrapper called")

    for youtube_id in youtube_ids:
        threading.current_thread().setName(f"ThreadYT/{youtube_id}")

        audio_file = f"{CWD_PATH}/backend/youtube_cache/{youtube_id}.mp3"
        target_file = f"{CWD_PATH}/frontend/public/audio/{youtube_id}.mp3"
        if os.path.exists(target_file):
            Log.trace(f"Frontend already has audio file for {youtube_id}")

        else:
            try:
                process_youtube(youtube_id)

            except ProcessBroke as ex:
                Log.error(f"YT process broke: {ex}")
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on process_audio.process_youtube", ex)
                continue

            # a = 1/0  # if this is commented it causes the client to refresh and miss the packet
            # TODO REACT REFRESHES IF FILE IS ADDED TO FRONTEND BECAUSE FILE WATCHER CHECKS THE FOLDER
            shutil.copyfile(audio_file, target_file)  # copy file to frontend for public use
            Log.trace("Copied audio file to frontend")
            # a = 1/0

        shove.latest_audio = f"audio/{youtube_id}.mp3"

        shove.send_packet_all_online("play_audio", {
            "author": "implement author",
            "url": f"audio/{youtube_id}.mp3"
        })


def process_youtube(args):
    youtube_id = args

    # threading.current_thread().setName(f"ProcessYT/{youtube_id}")
    # Log.trace(f"Started process for YouTube ID: {youtube_id}")
    cache = f"{CWD_PATH}/backend/youtube_cache"

    # todo benchmark -f \"bestaudio[filesize<3M]/bestaudio/best[filesize<3M]/best\" vs worstaudio/worst
    youtube_dl_command = " ".join([
        "youtube-dl",
        f"-o {cache}/%(id)s.%(ext)s",
        f"https://youtube.com/watch?v={youtube_id}",
        "--force-ipv4",  # ipv4 to fix stuck problem - https://www.reddit.com/r/youtubedl/comments/i7gqhu/youtubedl_stuck_at_downloading_webpage/
        "--format mp3/worstaudio/worst",
        f"--download-archive {cache}/archive.txt",
        "--no-warnings"
    ])

    Log.trace(f"Executing YTDL: {youtube_dl_command}")
    youtube_dl_now = time.time()
    # todo https://docs.python.org/3/library/subprocess.html#security-considerations
    youtube_dl_error = subprocess.call(youtube_dl_command, shell=True)
    Log.trace(f"YTDL command done in {round(time.time() - youtube_dl_now, 3)} s")

    if youtube_dl_error:
        raise ProcessBroke(f"Error on YTDL (process returned {youtube_dl_error})")

    filename = None
    for file in os.listdir(cache):
        if file.startswith(youtube_id):
            filename = file
            break
    # a = 1/0
    if not filename:
        raise ProcessBroke("Audio file missing from cache dir")

    if filename.endswith(".mp3"):  # no need to convert to mp3, done
        Log.trace("Downloaded/archived file is already .mp3")
        return

    # todo loudless normalization? "\"ffmpeg -i {} -c:a mp3 -filter:a loudnorm=i=-18:lra=17 -qscale:a 2 " + f"{audio_cache}/{ffmpeg_filename}" + " && del {}\""
    convert_command = " ".join([
        "ffmpeg",
        f"-i {cache}/{filename}",
        f"{cache}/{youtube_id}.mp3",
        "-loglevel warning"
    ])

    Log.trace(f"Not .mp3 file ({filename}), converting")
    convert_now = time.time()
    convert_error = subprocess.call(convert_command, shell=True)
    Log.trace(f"Convert done in {round(time.time() - convert_now, 3)} s, TOTAL: {round(time.time() - youtube_dl_now, 3)} s")

    if convert_error:
        raise ProcessBroke(f"Error on convert (process returned {convert_error})")

    os.remove(f"{cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")
