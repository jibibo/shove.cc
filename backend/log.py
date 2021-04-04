import traceback
import colorama
from colorama import Fore, Style

from convenience import *


colorama.init(autoreset=False)


LEVEL_TRACE = 0, "TRACE", ""
LEVEL_DEBUG = 1, "DEBUG", Fore.CYAN
LEVEL_INFO = 2, "INFO", Fore.GREEN + Style.BRIGHT
LEVEL_WARN = 3, "WARN", Fore.YELLOW
LEVEL_ERROR = 4, "ERROR", Fore.RED
LEVEL_FATAL = 5, "FATAL", Fore.RED + Style.BRIGHT
LEVEL_TEST = 6, "TEST", Fore.MAGENTA

# console logging
CONSOLE_LOG_LEVEL = LEVEL_TRACE
MESSAGE_LENGTH_CUTOFF = 400

# sound notification
SOUND_NOTIFICATION_LEVEL = LEVEL_WARN  # MUST BE HIGHER THAN LEVEL_TRACE, OR INFINITE LOGGING LOOP
SOUND_FILE = f"{CWD_PATH}/backend/audio/error.mp3"
IGNORE_SOUND_LEVELS: list = [LEVEL_TEST]

# file logging
FILE_LOG_LEVEL = LEVEL_WARN
LOG_TO_FILE = True
LOGS_DIRECTORY = f"{CWD_PATH}/backend/logs"
import pathlib
pathlib.Path().absolute()
LOG_FILE = f"{LOGS_DIRECTORY}/.latest.log"


class Log:
    PRINT_LOCK = threading.Lock()
    FILE_WRITING_QUEUE = Queue()  # now_str, level, thread_name, message, exception

    @staticmethod
    def trace(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_TRACE, exception, cutoff)

    @staticmethod
    def debug(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_DEBUG, exception, cutoff)

    @staticmethod
    def info(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_INFO, exception, cutoff)

    @staticmethod
    def warn(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_WARN, exception, cutoff)

    @staticmethod
    def error(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_ERROR, exception, cutoff)

    @staticmethod
    def fatal(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_FATAL, exception, cutoff)

    @staticmethod
    def test(message, exception=None, cutoff=True):
        Log._log(message, LEVEL_TEST, exception, cutoff)

    @staticmethod
    def _log(raw_message, level, exception=None, cutoff=True):
        raw_message = str(raw_message)
        thread_name = threading.current_thread().getName()
        now_console = datetime.now().strftime("%H:%M:%S")
        now_file = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        excess_message_size = len(raw_message) - MESSAGE_LENGTH_CUTOFF

        if cutoff and excess_message_size > 0:
            message = raw_message[:MESSAGE_LENGTH_CUTOFF] + f"... (+ {excess_message_size})"
        else:
            message = raw_message

        if level[0] >= CONSOLE_LOG_LEVEL[0]:  # check log level for console logging
            with Log.PRINT_LOCK:
                print(f"{level[2]}[{now_console}][{level[1]}][{thread_name}]{Style.RESET_ALL} {message}")
                if exception:
                    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stdout)

        if level[0] >= SOUND_NOTIFICATION_LEVEL[0] and level not in IGNORE_SOUND_LEVELS:
            # Log.trace(f"Playing sound {SOUND_FILE}")
            try:
                playsound.playsound(sound=SOUND_FILE, block=False)
            except playsound.PlaysoundException as ex:
                Log.trace(f"Sound exception caught: {ex}")

        if LOG_TO_FILE and level[0] >= FILE_LOG_LEVEL[0]:  # write raw message to file if enabled
            Log.FILE_WRITING_QUEUE.put((now_file, level, thread_name, raw_message, exception))

    @staticmethod
    def start_file_writer_thread():
        if LOG_TO_FILE:
            threading.Thread(target=Log.write_file_loop, name="LogFileWriter", daemon=True).start()

        else:
            Log.trace("Logging to file is DISABLED")

    @staticmethod
    def write_file_loop():
        try:
            open(LOG_FILE, "w").close()
            print(f"Emptied {LOG_FILE}")

        except FileNotFoundError:
            os.mkdir(LOGS_DIRECTORY)
            print(f"Created {LOGS_DIRECTORY}")
            open(LOG_FILE, "w").close()
            print(f"Created {LOG_FILE}")

        Log.trace("Ready")
        while True:
            now_str, level, thread_name, message, exception = Log.FILE_WRITING_QUEUE.get()

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}][{level[1]}][{thread_name}] {message}\n")
                if exception:
                    traceback.print_exception(type(exception), exception, exception.__traceback__, file=f)
