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
        Log.trace("Starting YT process")
        # process = multiprocessing.Process(target=process_youtube, args=(self.youtube_id,))

        for youtube_id in self.youtube_ids:
            threading.current_thread().setName(f"ThreadYT/{youtube_id}")

            try:
                # process.start()
                # process.join(self.timeout)
                process_youtube(youtube_id)  # use threading untill multiprocessing doesn't block anymore

            except ProcessBroke as ex:
                Log.error(f"YT process broke: {ex}")
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on process_audio.process_youtube", ex)
                continue

            # if process.is_alive():
            #     process.terminate()
            #     Log.warn(f"Terminated YT process (timeout exceeded: {self.timeout} s)")
            #
            #     # cleanup remaining non-mp3 file if process was killed
            #     for filename in os.listdir(f"{CWD_PATH}/backend/youtube_cache"):
            #         if filename.startswith(self.youtube_id) and not filename.endswith(".mp3"):
            #             os.remove(f"{CWD_PATH}/backend/youtube_cache/{filename}")
            #             Log.trace("Removed leftover non-mp3 audio file")
            #             break
            #
            #     return

            audio_file = f"{CWD_PATH}/backend/youtube_cache/{youtube_id}.mp3"
            target_file = f"{CWD_PATH}/frontend/public/audio/{youtube_id}.mp3"
            shutil.copyfile(audio_file, target_file)  # copy file to frontend for public use
            Log.trace("Copied audio file to frontend")

            self.shove.send_packet_all_online("play_audio", {
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
        "--force-ipv4",
        "--format mp3/worstaudio/worst",
        f"--download-archive {cache}/archive.txt",
        "--no-warnings"
    ])

    Log.trace(f"Executing YTDL: {youtube_dl_command}")
    youtube_dl_now = time.time()
    # todo sometimes hangs at "downloading webpage" -> SHOULD BE FIXED WITH IPV4
    # https://www.reddit.com/r/youtubedl/comments/i7gqhu/youtubedl_stuck_at_downloading_webpage/
    youtube_dl_error = os.system(youtube_dl_command)
    Log.trace(f"YTDL command done in {round(time.time() - youtube_dl_now, 3)} s")

    if youtube_dl_error:
        raise ProcessBroke(f"Error on YTDL (process returned {youtube_dl_error})")

    filename = None
    for file in os.listdir(cache):
        if file.startswith(youtube_id):
            filename = file
            break

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
    convert_error = os.system(convert_command)
    Log.trace(f"Convert done in {round(time.time() - convert_now, 3)} s, TOTAL: {round(time.time() - youtube_dl_now, 3)} s")

    if convert_error:
        raise ProcessBroke(f"Error on convert (process returned {convert_error})")

    os.remove(f"{cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")
