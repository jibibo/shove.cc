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
LOG_TO_FILE = False
MESSAGE_LENGTH_CUTOFF = 400
LOG_FILE = "/logs/_latest.log"


class Log:
    PRINT_LOCK = threading.Lock()
    FILE_WRITING_QUEUE = Queue()

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
        excess_message_size = len(message) - MESSAGE_LENGTH_CUTOFF
        if excess_message_size > 0:
            message = message[:MESSAGE_LENGTH_CUTOFF] + f"... (+ {excess_message_size})"

        thread_name = threading.current_thread().getName()
        now_str = datetime.now().strftime("%H:%M:%S")

        if level[0] >= CONSOLE_LOG_LEVEL[0]:  # check log level for console logging
            with Log.PRINT_LOCK:
                print(f"{level[2]}[{now_str}][{level[1]}]{Style.RESET_ALL}[{thread_name}] {message}")
                if exception:
                    # print(f"{Fore.CYAN}", end="")
                    traceback.print_exception(type(exception), exception, exception.__traceback__)
                    # print(f"{Style.RESET_ALL}", end="")

        if LOG_TO_FILE:  # file logging doesn't require specific log level
            Log.FILE_WRITING_QUEUE.put((now_str, level, thread_name, message))

    @staticmethod
    def start_file_writer_thread():
        threading.Thread(target=Log.write_to_log_file_thread, name="LogFileWriter", daemon=True).start()

    @staticmethod
    def write_to_log_file_thread():
        try:
            open(LOG_FILE, "w").close()
            print("Emptied latest log file")

        except FileNotFoundError:
            os.mkdir("/logs")
            print("Created /logs directory")
            open(LOG_FILE, "w").close()
            print("Created latest log file")

        Log.trace("Ready")
        while True:
            now_str, level, thread_name, message = Log.FILE_WRITING_QUEUE.get()

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}][SERVER/{level[1]}][{thread_name}] {message}\n")
