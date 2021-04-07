from convenience import *

from database import Song


def process_song_task(shove, youtube_id, user):
    set_greenthread_name(f"ProcessSong/{youtube_id}")
    Log.trace(f"Processing ID {youtube_id}")

    # ---> we arrive here with the youtube id that was requested
    # check if database has an entry, which means backend cache has it
    #   if no, download the song, convert and create db entry
    # then check if the file exists in frontend
    #   if no, copy the file to frontend
    # done

    backend_audio_file = f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}/{youtube_id}.mp3"
    frontend_audio_file = f"{CWD_PATH}/{FRONTEND_AUDIO_CACHE}/{youtube_id}.mp3"

    try:
        song = shove.songs.find_single(song_id=youtube_id)

    except DatabaseEntryNotFound:
        Log.test("Database entry missing, downloading and converting")

        try:
            duration, name = extract_and_check_song_info(youtube_id)  # extract video information and check duration
        except ExtractSongInformationFailed as ex:
            Log.error(f"Song information extraction failed: {ex}", ex)
            shove.send_packet_to(user, "error", error_packet("Song information extraction failed"))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on extract_and_check_song_info", ex)
            shove.send_packet_to(user, "error", error_packet("Song information extraction failed"))
            return

        try:
            download_time = download_youtube_audio(youtube_id)  # download with YTDL
        except DownloadSongFailed as ex:
            Log.error(f"Song download failed, update youtube-dl?: {ex}", ex)
            shove.send_packet_to(user, "error", error_packet("Song download failed"))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on download_youtube_audio", ex)
            shove.send_packet_to(user, "error", error_packet("Song download failed"))
            return

        try:
            convert_time = convert_youtube_audio(youtube_id)  # convert to mp3
        except ConvertSongFailed as ex:
            Log.error(f"Song converting failed, update youtube-dl?: {ex}", ex)
            shove.send_packet_to(user, "error", error_packet("Song converting failed"))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on convert_youtube_audio", ex)
            shove.send_packet_to(user, "error", error_packet("Song converting failed"))
            return

        if not os.path.exists(backend_audio_file):
            Log.error("Backend audio file is missing")
            return

        duration = MP3(f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}/{youtube_id}.mp3").info.length
        song = Song(
            shove.songs,
            convert_time=convert_time,
            download_time=download_time,
            duration=duration,
            name=name,
            platform="youtube",
            song_id=youtube_id,
        )

    else:
        Log.test("Database entry found")

    Log.trace("Setting song and sending packet")
    song.copy_to_frontend_if_absent()
    shove.latest_song = song
    shove.latest_song_author = user.get_username()
    song.increment_plays(shove.get_user_count())
    shove.send_packet_to_everyone("play_song", {
        "author": user.get_username(),
        "name": song["name"],
        "plays": song["plays"],
        "url": shove.latest_song.get_url()
    })


def extract_and_check_song_info(youtube_id) -> tuple:
    url = f"https://youtube.googleapis.com/youtube/v3/videos"
    params = {  # url request parameters
        "key": YOUTUBE_API_KEY,
        "part": "contentDetails,snippet,statistics",
        "id": youtube_id
    }
    Log.trace(f"Sending YT API request")

    response = requests.get(url, params=params, timeout=1).json()  # https://stackoverflow.com/a/21966169/13216113 timeout kw fixes 20 s request bug?
    Log.trace(f"Response: {response}")

    if not response:
        raise ExtractSongInformationFailed("No response from YT API (not good)")

    if not response["items"]:
        raise ExtractSongInformationFailed("No songs found")

    song = response["items"][0]
    name = song["snippet"]["title"]
    duration = isodate.parse_duration(song["contentDetails"]["duration"]).total_seconds()  # https://stackoverflow.com/a/16743442/13216113

    if duration > 300:
        raise ExtractSongInformationFailed("Song duration is more than 5 minutes")

    return duration, name


def download_youtube_audio(youtube_id) -> float:
    """Downloads the youtube song and returns the time it took to download"""

    Log.trace(f"Downloading audio: youtube_id={youtube_id}")
    backend_cache = f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}"

    # todo benchmark -f \"bestaudio[filesize<3M]/bestaudio/best[filesize<3M]/best\" vs worstaudio/worst
    # youtube_dl_command1 = " ".join([  # log available formats
    #     "youtube-dl",
    #     f"https://youtube.com/watch?v={youtube_id}",
    #     "--force-ipv4",
    #     "-F"
    # ])
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
    youtube_dl_error1 = 0  # subprocess.call(youtube_dl_command1, shell=True)
    youtube_dl_error2 = subprocess.call(youtube_dl_command2, shell=True)
    download_time = time.time() - start_time
    Log.trace(f"YTDL done in {round(download_time, 3)} s")

    if youtube_dl_error1 or youtube_dl_error2:
        raise DownloadSongFailed(f"Subprocess returned {youtube_dl_error1 or youtube_dl_command2}")

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
        raise ConvertSongFailed("Audio file missing from backend cache dir")

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
        raise ConvertSongFailed(f"Subprocess returned {convert_error}")

    os.remove(f"{backend_cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")

    return convert_time