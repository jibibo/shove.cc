# Socket settings
HOST = "0.0.0.0"
PORT = 777


# Startup
STARTUP_EMPTY_FRONTEND_CACHE = True
STARTUP_CLEANUP_BACKEND_CACHE = True
DELAY_BEFORE_RESTART = 20


# User pinging
PING_USERS_ENABLED = False
PING_USERS_INTERVAL = 5  # seconds
PONG_DELAY_BEFORE_TIMEOUT = 5  # todo fix: timeout < interval should be possible


# What to log todo use logging module for proper logging?
LOG_SOCKETIO = False
LOG_ENGINEIO = False
LOG_WSGI = False
LOG_YOUTUBE_DL_VERBOSE = False
LOG_YOUTUBE_DL_WARNINGS = False


# Console logging
CONSOLE_LOGGING_LEVEL = "TRACE"
CONSOLE_LOGGING_LENGTH_CUTOFF = 800


# Audio caches
BACKEND_AUDIO_CACHE = "backend/audio_cache"
FRONTEND_AUDIO_CACHE = "frontend/public/audio"


# Sound notifications
ERROR_SOUND_NOTIFICATION_LEVEL = "WARN"
ERROR_SOUND_FILE_PATH = "backend/audio/error.mp3"
ERROR_SOUND_IGNORE_LEVELS: list = ["TEST"]


# File logging
ENABLE_FILE_LOGGING = True
FILE_LOGGING_LEVEL = "WARN"
LOGS_DIRECTORY = "backend/logs"
LATEST_LOG_FILENAME = ".latest.log"
