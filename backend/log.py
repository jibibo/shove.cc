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
CONSOLE_LOG_LEVEL = LEVEL_TRACE
LOG_TO_FILE = True
MESSAGE_LENGTH_CUTOFF = 1000
LOGS_DIRECTORY = "backend/logs"
LOG_FILE = f"{LOGS_DIRECTORY}/_latest.log"


class Log:
    PRINT_LOCK = threading.Lock()
    FILE_WRITING_QUEUE = Queue()  # now_str, level, thread_name, message

    @staticmethod
    def trace(message, exception=None):
        Log.log(message, level=LEVEL_TRACE, exception=exception)

    @staticmethod
    def debug(message, exception=None):
        Log.log(message, level=LEVEL_DEBUG, exception=exception)

    @staticmethod
    def info(message, exception=None):
        Log.log(message, level=LEVEL_INFO, exception=exception)

    @staticmethod
    def warn(message, exception=None):
        Log.log(message, level=LEVEL_WARN, exception=exception)

    @staticmethod
    def error(message, exception=None):
        Log.log(message, level=LEVEL_ERROR, exception=exception)

    @staticmethod
    def fatal(message, exception=None):
        Log.log(message, level=LEVEL_FATAL, exception=exception)

    @staticmethod
    def test(message, exception=None):
        Log.log(message, level=LEVEL_TEST, exception=exception)

    @staticmethod
    def log(message, level, exception=None):
        message = str(message)
        excess_message_size = len(message) - MESSAGE_LENGTH_CUTOFF
        if excess_message_size > 0:
            message = message[:MESSAGE_LENGTH_CUTOFF] + f"... (+ {excess_message_size})"

        thread_name = threading.current_thread().getName()
        now_str = datetime.now().strftime("%H:%M:%S")

        if level[0] >= CONSOLE_LOG_LEVEL[0]:  # check log level for console logging
            with Log.PRINT_LOCK:
                print(f"{level[2]}[{now_str}][{level[1]}][{thread_name}]{Style.RESET_ALL} {message}")
                if exception:
                    # traceback.print_exc()
                    traceback.print_exception(type(exception), exception, exception.__traceback__)

        if LOG_TO_FILE:  # file logging doesn't require specific log level
            Log.FILE_WRITING_QUEUE.put((now_str, level, thread_name, message))

    @staticmethod
    def start_file_writer_thread():
        if LOG_TO_FILE:
            threading.Thread(target=Log._file_writer_thread, name="LogFileWriter", daemon=True).start()

        else:
            print("Logging to file is DISABLED")

    @staticmethod
    def _file_writer_thread():  # todo broken
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
            now_str, level, thread_name, message = Log.FILE_WRITING_QUEUE.get()

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}][{level[1]}][{thread_name}] {message}\n")
