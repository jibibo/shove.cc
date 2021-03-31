from convenience import *


def remove_non_mp3_files_from_cache():
    for filename in os.listdir(f"{CWD_PATH}/backend/youtube_cache"):
        if not (filename.endswith(".mp3") or filename.endswith(".txt")):
            os.remove(f"{CWD_PATH}/backend/youtube_cache/{filename}")

    Log.trace("Removed all files that weren't .mp3 or .txt from backend/youtube_cache")


def clear_frontend_audio_cache():
    for filename in os.listdir(f"{CWD_PATH}/frontend/public/audio"):
        os.remove(f"{CWD_PATH}/frontend/public/audio/{filename}")

    Log.trace("Removed all files in frontend/audio")