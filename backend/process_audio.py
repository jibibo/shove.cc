from convenience import *


class ProcessBroke(Exception):
    pass


class ProcessYoutubeThread(threading.Thread):
    def __init__(self, shove, youtube_id, timeout):
        super().__init__(name=f"ThreadYT/{youtube_id}", daemon=True)
        self.shove = shove
        self.youtube_id = youtube_id
        self.timeout = timeout

    def run(self):
        Log.trace("Starting YT process")
        process = multiprocessing.Process(target=process_youtube, args=(self.youtube_id,))

        try:
            process.start()
            process.join(self.timeout)

        except ProcessBroke as ex:
            Log.error(f"YT process broke", ex)
            return

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on process_audio.process_youtube", ex)
            return

        if process.is_alive():
            process.terminate()
            Log.warn(f"Terminated YT process (timeout exceeded: {self.timeout})")
            return

        audio_file = f"{CWD_PATH}/backend/youtube_cache/{self.youtube_id}.mp3"
        target_file = f"{CWD_PATH}/frontend/public/audio/{self.youtube_id}.mp3"
        shutil.copyfile(audio_file, target_file)
        Log.trace("Copied audio file to frontend")

        self.shove.send_packet_all_online("play_audio", {
            "author": "implement author",
            "url": f"audio/{self.youtube_id}.mp3"
        })


def process_youtube(args):
    youtube_id = args

    threading.current_thread().setName(f"ProcessYT/{youtube_id}")
    Log.trace(f"Started process for YouTube ID: {youtube_id}")
    cache = f"{CWD_PATH}/backend/youtube_cache"

    # todo benchmark -f \"bestaudio[filesize<3M]/bestaudio/best[filesize<3M]/best\" vs worstaudio/worst
    youtube_dl_command = f"youtube-dl " \
                         f"-o {cache}/{youtube_id}.%(ext)s " \
                         f"-f mp3/worstaudio/worst " \
                         f"--download-archive {cache}/archive.txt " \
                         f"https://youtube.com/watch?v={youtube_id}"

    Log.trace(f"Executing YTDL command")
    youtube_dl_now = time.time()
    # todo sometimes hangs at "downloading webpage" - possibly because of socketio main thread?
    youtube_dl_error = os.system(youtube_dl_command)
    Log.trace(f"YTDL command done in {round(time.time() - youtube_dl_now, 3)}s")

    if youtube_dl_error:
        raise ProcessBroke(f"Error on YTDL (command returned {youtube_dl_error})")

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

    # for loudless normalization? "\"ffmpeg -i {} -c:a mp3 -filter:a loudnorm=i=-18:lra=17 -qscale:a 2 " + f"{audio_cache}/{ffmpeg_filename}" + " && del {}\""
    convert_command = f"ffmpeg " \
                      f"-i {cache}/{filename} " \
                      f"{cache}/{youtube_id}.mp3 " \
                      f"-loglevel warning"

    Log.trace(f"Not .mp3 file, converting with command")
    convert_now = time.time()
    convert_error = os.system(convert_command)
    Log.trace(f"Convert command done in {round(time.time() - convert_now, 3)}s, TOTAL: {round(time.time() - youtube_dl_now, 3)}")

    if convert_error:
        raise ProcessBroke(f"Error on convert (command returned {convert_error})")

    os.remove(f"{cache}/{filename}")
    Log.trace(f"Deleted old file {cache}/{filename}")
