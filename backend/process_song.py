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

    try:
        song = shove.songs.find_single(song_id=youtube_id)  # if the song exists in the database, we're done here

    except DatabaseEntryNotFound:  # song not in database (yet)
        Log.trace("DB entry missing - downloading and converting")

        try:
            duration, name = extract_and_check_song_info(youtube_id)  # extract video information and check duration
        except ExtractSongInformationFailed as ex:  # these errors should not contain sensitive information!
            Log.trace(f"Song info extraction failed: {ex}")
            shove.send_packet_to(user, "error", error_packet(str(ex)))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on extract_and_check_song_info", ex)
            shove.send_packet_to(user, "error", error_packet("Song info extraction failed"))
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
            Log.error(f"Song conversion failed, update youtube-dl?: {ex}", ex)
            shove.send_packet_to(user, "error", error_packet("Song conversion failed"))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on convert_youtube_audio", ex)
            shove.send_packet_to(user, "error", error_packet("Song conversion failed"))
            return

        backend_audio_file = f"{CWD_PATH}/{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}/{youtube_id}.mp3"
        if not os.path.exists(backend_audio_file):
            Log.fatal("Backend audio file is missing?")  # shouldn't ever happen
            return

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
        Log.trace("DB entry found")

    song.play(shove, user)


def extract_and_check_song_info(youtube_id) -> tuple:
    """Extract video information, check, and return a tuple"""

    url = f"https://youtube.googleapis.com/youtube/v3/videos"
    params = {  # url request parameters
        "key": YOUTUBE_API_KEY,
        "part": "contentDetails,snippet,statistics",
        "id": youtube_id
    }
    Log.trace(f"Sending YT API request")

    response = requests.get(url, params=params, timeout=1).json()  # https://stackoverflow.com/a/21966169/13216113 timeout keyword fixes slow request
    Log.trace(f"YT API response: {response}")

    if not response:
        raise ExtractSongInformationFailed("No response from YT API")

    if not response["items"]:
        raise ExtractSongInformationFailed("No songs found - invalid ID?")

    song = response["items"][0]
    name = song["snippet"]["title"]
    duration = isodate.parse_duration(song["contentDetails"]["duration"]).total_seconds()  # https://stackoverflow.com/a/16743442/13216113

    if duration > SONG_MAX_DURATION:
        raise ExtractSongInformationFailed(f"Song duration exceeds maximum ({SONG_MAX_DURATION} s)")

    return duration, name


def download_youtube_audio(youtube_id) -> float:
    """Downloads the youtube song and returns the time it took to download"""

    backend_cache = f"{CWD_PATH}/{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}"

    for file in os.listdir(backend_cache):
        if file.startswith(youtube_id):  # already downloaded a file (not necessarily mp3) for the given song id
            Log.trace("Found existing file in backend, not downloading")
            return 0

    Log.trace(f"Downloading song: youtube_id={youtube_id}")

    youtube_dl_command = " ".join([  # actually download it
        "youtube-dl",
        f"-o {backend_cache}/%(id)s.%(ext)s",
        f"https://youtube.com/watch?v={youtube_id}",
        "--force-ipv4",  # ipv4 to fix hanging bug - https://www.reddit.com/r/youtubedl/comments/i7gqhu/youtubedl_stuck_at_downloading_webpage/
        "--format mp3/bestaudio",  # if downloading mp3 is an option, try that (saves time converting to mp3)
        # "--user-agent \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",  # might prevent some errors, not certain
        "--verbose" if LOG_YOUTUBE_DL_VERBOSE else "",
        "--no-warnings" if not LOG_YOUTUBE_DL_WARNINGS else "",
    ])

    start_time = time.time()
    # todo possibily dangerous, see https://docs.python.org/3/library/subprocess.html#security-considerations
    youtube_dl_error = subprocess.call(youtube_dl_command, shell=True)
    download_time = time.time() - start_time
    Log.trace(f"YTDL done in {round(download_time, 3)} s")

    if youtube_dl_error:
        raise DownloadSongFailed(f"Subprocess returned {youtube_dl_command}")

    return download_time


def convert_youtube_audio(youtube_id) -> float:
    """Converts the file in the backend to .mp3 (compatible with HTML <audio>)"""

    backend_cache = f"{CWD_PATH}/{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}"

    filename = None
    for file in os.listdir(backend_cache):
        if file.startswith(youtube_id):
            filename = file
            break

    if not filename:
        raise ConvertSongFailed("Song file missing from backend cache")

    if filename.endswith(".mp3"):  # no need to convert to mp3, done
        Log.trace("Downloaded file in backend cache is already .mp3, not converting")
        return 0

    Log.trace(f"Converting file to mp3: youtube_id={youtube_id}")

    # todo loudless normalization? "\"ffmpeg -i {} -c:a mp3 -filter:a loudnorm=i=-18:lra=17 -qscale:a 2 " + f"{cache}/{ffmpeg_filename}""
    convert_command = " ".join([
        "ffmpeg",
        f"-i {backend_cache}/{filename}",
        f"{backend_cache}/{youtube_id}.mp3",
        f"-loglevel {FFMPEG_LOGGING_LEVEL}"
    ])

    start_time = time.time()
    convert_error = subprocess.call(convert_command, shell=True)
    convert_time = time.time() - start_time
    Log.trace(f"Convert done in {round(convert_time, 3)} s")

    if convert_error:
        raise ConvertSongFailed(f"Subprocess returned {convert_error}")

    os.remove(f"{backend_cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")

    return convert_time