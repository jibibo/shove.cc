from convenience import *


def process_song_task(shove, youtube_id: str, user):
    set_greenthread_name(f"ProcessSong/{youtube_id}")
    Log.trace(f"Processing ID {youtube_id}")

    # make sure the youtube_id is absolutely safe to prevent abuse of subprocess.Popen

    if len(youtube_id) != YOUTUBE_ID_LENGTH:
        Log.warn(f"Invalid youtube id length: {len(youtube_id)}, ignoring call")
        shove.send_packet_to(user, "error", error_packet("Invalid ID length"))
        return

    for char in youtube_id:
        if char not in YOUTUBE_ID_CHARACTERS:
            Log.warn(f"Invalid char in youtube id: {char}, ignoring call")
            shove.send_packet_to(user, "error", error_packet("Invalid character in ID"))
            return

    try:
        # if the song exists in the database, we're done here
        song = shove.songs.find_single(song_id=youtube_id)

    except DatabaseEntryNotFound:  # song not in database (yet)
        Log.trace("DB entry missing - downloading and converting")

        try:
            # extract video information and check duration
            duration, name = extract_and_check_song_info(youtube_id)
        except ExtractSongInformationFailed as ex:
            # these errors should not contain sensitive information
            # as description gets sent to user
            Log.trace(f"Song info extraction failed: {ex}")
            shove.send_packet_to(user, "error", error_packet(str(ex)))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on extract_and_check_song_info", ex)
            shove.send_packet_to(user, "error", error_packet("Song info extraction failed"))
            return

        try:
            # download with YTDL
            download_time = download_youtube_audio(youtube_id)
        except SubprocessFailed as ex:
            Log.error(f"Song download failed, update youtube-dl?: {ex}", ex)
            shove.send_packet_to(user, "error", error_packet("Song download failed"))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on download_youtube_audio", ex)
            shove.send_packet_to(user, "error", error_packet("Song download failed"))
            return

        try:
            # convert to mp3
            convert_time = convert_youtube_audio(youtube_id)
        except SubprocessFailed as ex:
            Log.error(f"File conversion failed, update youtube-dl?: {ex}", ex)
            shove.send_packet_to(user, "error", error_packet("File conversion failed"))
            return
        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on convert_youtube_audio", ex)
            shove.send_packet_to(user, "error", error_packet("File conversion failed"))
            return

        # double check if backend has the song mp3 file
        backend_audio_file = f"{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}/{youtube_id}.mp3"
        if not os.path.exists(backend_audio_file):
            raise RuntimeError("Song file missing from backend songs folder")

        song = shove.songs.create_entry(
            convert_time=convert_time,
            download_time=download_time,
            duration=duration,
            name=name,
            platform="youtube",
            song_id=youtube_id
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

    # https://stackoverflow.com/a/21966169/13216113 timeout keyword fixes slow request
    response = requests.get(url, params=params, timeout=1).json()
    Log.trace(f"YT API response: {response}")

    if not response:
        raise ExtractSongInformationFailed("No response from YT API")

    if not response["items"]:
        raise ExtractSongInformationFailed(f"No songs found with ID {youtube_id}")

    song = response["items"][0]
    name = song["snippet"]["title"]
    # isodate https://stackoverflow.com/a/16743442/13216113
    duration = isodate.parse_duration(song["contentDetails"]["duration"]).total_seconds()

    if duration > SONG_MAX_DURATION:
        raise ExtractSongInformationFailed(f"Song duration exceeds maximum ({SONG_MAX_DURATION} s)")

    return duration, name


def download_youtube_audio(youtube_id) -> float:
    """Downloads the youtube song and returns the time it took to download"""

    Log.trace(f"Downloading song")
    backend_cache = f"{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}"

    for file in os.listdir(backend_cache):
        if file.startswith(youtube_id):  # already downloaded a file (not necessarily mp3) for the given song id
            Log.trace("Found existing file in backend, not downloading")
            return 0

    args = [
        f"https://youtube.com/watch?v={youtube_id}",
        f"-o {backend_cache}/%(id)s.%(ext)s",
        "-f mp3/bestaudio",  # if downloading mp3 is an option, try that (saves time converting to mp3)
        "--force-ipv4",  # ipv4 to fix hanging bug - https://www.reddit.com/r/youtubedl/comments/i7gqhu/youtubedl_stuck_at_downloading_webpage/
        # "--user-agent \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",  # might prevent some errors, not certain
    ]

    if LOG_YOUTUBE_DL_VERBOSE:
        args.append("-v")
    if not LOG_YOUTUBE_DL_WARNINGS:
        args.append("--no-warnings")

    download_time = call_subprocess(  # download file with youtube-dl
        "youtube-dl",
        *args
    )

    return download_time


def convert_youtube_audio(youtube_id) -> float:
    """Converts the file in the backend to .mp3 (compatible with HTML <audio>)"""

    Log.trace(f"Converting file to mp3")
    backend_cache = f"{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}"

    filename = None
    for file in os.listdir(backend_cache):
        if file.startswith(youtube_id):
            filename = file
            break

    if not filename:
        raise RuntimeError("Song file missing from backend songs folder")

    if filename.endswith(".mp3"):  # no need to convert to mp3, done
        Log.trace("Downloaded file in backend cache is already .mp3, not converting")
        return 0

    convert_time = call_subprocess(
        "ffmpeg",
        f"-i {backend_cache}/{filename}",
        f"{backend_cache}/{youtube_id}.mp3",
        f"-loglevel {FFMPEG_LOGGING_LEVEL}"
    )

    os.remove(f"{backend_cache}/{filename}")
    Log.trace(f"Deleted old file {filename}")

    return convert_time


def call_subprocess(command, *args) -> float:
    """Executes a command supplied with args in shell.
    Returns the time it took to execute the command.
    Raises SubprocessFailed on failure."""

    args = " ".join(args)
    finalized_command = f"{command} {args}"
    Log.trace(f"Starting subprocess '{command}', finalized: '{finalized_command}'")

    start_time = time.time()
    # should be 100% safe, according to docs: https://docs.python.org/3/library/subprocess.html#security-considerations
    return_code = subprocess.call(finalized_command)
    elapsed_time = time.time() - start_time

    if return_code != 0:
        raise SubprocessFailed(f"Subprocess {command} failed, code: {return_code}")

    Log.trace(f"Subprocess '{command}' done in {round(elapsed_time, 3)} s")
    return elapsed_time
