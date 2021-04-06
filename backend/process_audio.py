from convenience import *

# todo set backend and frontend audio directories in config.py


def process_youtube_ids_audio_task(shove, youtube_ids, user):
    # threading.current_thread().setName("ProcessAudio")
    Log.trace("Started YT audio task")

    for youtube_id in youtube_ids:
        # threading.current_thread().setName(f"ProcessAudio/{youtube_id}")
        Log.trace(f"Processing YT ID {youtube_id}")

        audio_file = f"{CWD_PATH}/backend/youtube_cache/{youtube_id}.mp3"
        target_file = f"{CWD_PATH}/frontend/public/audio/{youtube_id}.mp3"
        if os.path.exists(target_file):
            Log.trace(f"Frontend already has audio file for {youtube_id}, only going to send url")

        else:
            try:
                download_youtube_audio(youtube_id)  # download with YTDL

            except DownloadAudioFailed as ex:
                Log.error(f"Download audio failed: {ex}, update youtube-dl?", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio processing failed"))
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on process_audio.download_youtube_audio", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio processing failed"))
                continue

            try:
                convert_youtube_audio(youtube_id)  # convert to mp3

            except ConvertAudioFailed as ex:
                Log.error(f"Convert audio failed: {ex}, update youtube-dl?", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio processing failed"))
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on process_audio.convert_youtube_audio", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio processing failed"))
                continue

            Log.trace("Copying audio file to frontend")
            shutil.copyfile(audio_file, target_file)  # copy file to frontend for public access

        shove.latest_audio_author = user.get_username()
        shove.latest_audio_url = f"audio/{youtube_id}.mp3"
        shove.send_packet_to_everyone("play_audio", {
            "author": user.get_username(),
            "url": shove.latest_audio_url
        })


def download_youtube_audio(youtube_id):
    Log.trace(f"Downloading audio: youtube_id={youtube_id}")
    cache = f"{CWD_PATH}/backend/youtube_cache"

    # todo benchmark -f \"bestaudio[filesize<3M]/bestaudio/best[filesize<3M]/best\" vs worstaudio/worst
    youtube_dl_command = " ".join([
        "youtube-dl",
        f"-o {cache}/%(id)s.%(ext)s",
        f"https://youtube.com/watch?v={youtube_id}",
        "--force-ipv4",  # ipv4 to fix hanging bug - https://www.reddit.com/r/youtubedl/comments/i7gqhu/youtubedl_stuck_at_downloading_webpage/
        "--format mp3/worstaudio/worst",  # if downloading mp3 is an option, try that (saves time converting to mp3)
        f"--download-archive {cache}/archive.txt",
        # "--no-warnings",
        # "--user-agent \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",  # might prevent some errors, not certain
        "--verbose"
    ])

    Log.trace(f"Calling YTDL subprocess: {youtube_dl_command}")
    start_time = time.time()
    # todo possibily dangerous, see https://docs.python.org/3/library/subprocess.html#security-considerations
    youtube_dl_error = subprocess.call(youtube_dl_command, shell=True)
    Log.trace(f"YTDL done in {round(time.time() - start_time, 3)} s")

    if youtube_dl_error:
        raise DownloadAudioFailed(f"Subprocess returned {youtube_dl_error}")


def convert_youtube_audio(youtube_id):
    Log.trace(f"Converting audio to mp3: youtube_id={youtube_id}")
    cache = f"{CWD_PATH}/backend/youtube_cache"

    filename = None
    for file in os.listdir(cache):
        if file.startswith(youtube_id):
            filename = file
            break

    if not filename:
        raise ConvertAudioFailed("Audio file missing from backend cache dir")

    if filename.endswith(".mp3"):  # no need to convert to mp3, done
        Log.trace("Downloaded file in backend cache is already .mp3, not converting")
        return

    # todo loudless normalization? "\"ffmpeg -i {} -c:a mp3 -filter:a loudnorm=i=-18:lra=17 -qscale:a 2 " + f"{audio_cache}/{ffmpeg_filename}" + " && del {}\""
    convert_command = " ".join([
        "ffmpeg",
        f"-i {cache}/{filename}",
        f"{cache}/{youtube_id}.mp3",
        "-loglevel warning"
    ])

    Log.trace(f"Calling ffmpeg convert subprocess: {convert_command}")
    start_time = time.time()
    convert_error = subprocess.call(convert_command, shell=True)
    Log.trace(f"Convert done in {round(time.time() - start_time, 3)} s")

    if convert_error:
        raise ConvertAudioFailed(f"Subprocess returned {convert_error}")

    os.remove(f"{cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")
