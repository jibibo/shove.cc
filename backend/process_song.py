from convenience import *

from song import Song


def process_song_task(shove, youtube_ids, names, user):
    set_greenthread_name("ProcessSong")
    Log.trace("Started process song task")

    for youtube_id, name in zip(youtube_ids, names):
        set_greenthread_name(f"ProcessSong/{youtube_id}")
        Log.trace(f"Processing ID {youtube_id}: {name}")

        backend_audio_file = f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}/{youtube_id}.mp3"
        frontend_audio_file = f"{CWD_PATH}/{FRONTEND_AUDIO_CACHE}/{youtube_id}.mp3"

        # todo split this up, first check backend, then check frontend (backend should always have the file!, not frontend)
        # todo frontend can sometimes not load audio, does it exist in frontend?
        if os.path.exists(backend_audio_file) and os.path.exists(frontend_audio_file):
            Log.trace(f"Backend and frontend already have mp3 file for {youtube_id}, skipping downloading and converting")

        else:
            Log.trace(f"Backend/frontend does not have mp3 file for {youtube_id}")

            try:
                download_time = download_youtube_audio(youtube_id)  # download with YTDL

            except DownloadAudioFailed as ex:
                Log.error(f"Download audio failed, update youtube-dl?: {ex}", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio download failed"))
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on download_youtube_audio", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio download failed"))
                continue

            try:
                convert_time = convert_youtube_audio(youtube_id)  # convert to mp3

            except ConvertAudioFailed as ex:
                Log.error(f"Convert audio failed, update youtube-dl?: {ex}", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio converting failed"))
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on convert_youtube_audio", ex)
                shove.send_packet_to(user, "error", default_error_packet(description="Audio converting failed"))
                continue

            duration = MP3(f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}/{youtube_id}.mp3").info.length
            Log.trace("Copying audio file to frontend")
            shutil.copyfile(backend_audio_file, frontend_audio_file)  # copy file to frontend for public access
            song = Song("youtube", youtube_id, name, duration, download_time, convert_time)
            shove.add_song(song)

        Log.trace("Setting song data and sending packet")
        song = shove.get_song_by_id(youtube_id)
        shove.latest_song = song
        shove.latest_song_author = user.get_username()
        song.increment_plays(shove.get_user_count())
        shove.send_packet_to_everyone("play_song", {
            "author": user.get_username(),
            "name": shove.latest_song.name,
            "plays": song.plays,
            "url": shove.latest_song.url
        })


def download_youtube_audio(youtube_id) -> float:
    """Downloads the youtube song and returns the time it took to download"""

    Log.trace(f"Downloading audio: youtube_id={youtube_id}")
    backend_cache = f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}"

    # todo benchmark -f \"bestaudio[filesize<3M]/bestaudio/best[filesize<3M]/best\" vs worstaudio/worst
    youtube_dl_command1 = " ".join([  # log available formats
        "youtube-dl",
        f"https://youtube.com/watch?v={youtube_id}",
        "--force-ipv4",
        "-F"
    ])
    youtube_dl_command2 = " ".join([  # actually download it
        "youtube-dl",
        f"-o {backend_cache}/%(id)s.%(ext)s",
        f"https://youtube.com/watch?v={youtube_id}",
        "--force-ipv4",  # ipv4 to fix hanging bug - https://www.reddit.com/r/youtubedl/comments/i7gqhu/youtubedl_stuck_at_downloading_webpage/
        "--format mp3/bestaudio",  # if downloading mp3 is an option, try that (saves time converting to mp3)
        f"--download-archive {backend_cache}/archive.txt",
        # "--user-agent \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",  # might prevent some errors, not certain
        "--verbose" if LOG_YOUTUBE_DL_VERBOSE else "",
        "--no-warnings" if not LOG_YOUTUBE_DL_WARNINGS else "",
    ])

    Log.trace(f"Calling YTDL subprocess")
    start_time = time.time()
    # todo possibily dangerous, see https://docs.python.org/3/library/subprocess.html#security-considerations
    youtube_dl_error1 = subprocess.call(youtube_dl_command1, shell=True)
    youtube_dl_error2 = subprocess.call(youtube_dl_command2, shell=True)
    download_time = time.time() - start_time
    Log.trace(f"YTDL done in {round(download_time, 3)} s")

    if youtube_dl_error1 or youtube_dl_error2:
        raise DownloadAudioFailed(f"Subprocess returned {youtube_dl_error1 or youtube_dl_command2}")

    return download_time


def convert_youtube_audio(youtube_id) -> float:
    Log.trace(f"Converting audio to mp3: youtube_id={youtube_id}")
    backend_cache = f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}"

    filename = None
    for file in os.listdir(backend_cache):
        if file.startswith(youtube_id):
            filename = file
            break

    if not filename:
        raise ConvertAudioFailed("Audio file missing from backend cache dir")

    if filename.endswith(".mp3"):  # no need to convert to mp3, done todo doesn't return a converting time
        Log.trace("Downloaded file in backend cache is already .mp3, not converting")
        return 0.0

    # todo loudless normalization? "\"ffmpeg -i {} -c:a mp3 -filter:a loudnorm=i=-18:lra=17 -qscale:a 2 " + f"{audio_cache}/{ffmpeg_filename}" + " && del {}\""
    convert_command = " ".join([
        "ffmpeg",
        f"-i {backend_cache}/{filename}",
        f"{backend_cache}/{youtube_id}.mp3",
        "-loglevel warning"
    ])

    Log.trace(f"Calling ffmpeg convert subprocess")
    start_time = time.time()
    convert_error = subprocess.call(convert_command, shell=True)
    convert_time = time.time() - start_time
    Log.trace(f"Convert done in {round(convert_time, 3)} s")

    if convert_error:
        raise ConvertAudioFailed(f"Subprocess returned {convert_error}")

    os.remove(f"{backend_cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")

    return convert_time