from convenience import *


colorama.init(autoreset=False)

ERROR_SOUND_ABS = f"{CWD_PATH}/{ERROR_SOUND_FILE_PATH}"


class LogLevel:
    TRACE = 0, "TRACE", ""
    DEBUG = 1, "DEBUG", Fore.CYAN
    INFO = 2, "INFO", Fore.GREEN + Style.BRIGHT
    WARN = 3, "WARN", Fore.YELLOW
    ERROR = 4, "ERROR", Fore.RED
    FATAL = 5, "FATAL", Fore.RED + Style.BRIGHT
    TEST = 6, "TEST", Fore.MAGENTA

    @staticmethod
    def get_level_int(level_str: str):
        for level in LogLevel.get_all_levels():
            if level[1] == level_str:
                return level[0]

        raise ValueError(f"Unknown level string provided: {level_str}")

    @staticmethod
    def get_all_levels():
        return [LogLevel.TRACE, LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN,
                LogLevel.ERROR, LogLevel.FATAL, LogLevel.TEST]


class Log:
    FILE_WRITING_QUEUE = Queue()  # now_str, level, thread_name, message, exception

    @staticmethod
    def trace(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.TRACE, exception, cutoff)

    @staticmethod
    def debug(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.DEBUG, exception, cutoff)

    @staticmethod
    def info(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.INFO, exception, cutoff)

    @staticmethod
    def warn(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.WARN, exception, cutoff)

    @staticmethod
    def error(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.ERROR, exception, cutoff)

    @staticmethod
    def fatal(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.FATAL, exception, cutoff)

    @staticmethod
    def test(message, exception=None, cutoff=True):
        Log._log(message, LogLevel.TEST, exception, cutoff)

    @staticmethod
    def _log(raw_message, level, exception=None, cutoff=True):
        raw_message = str(raw_message)

        try:
            # dirty way of setting/getting Greenthread names, as threading.current_thread().getName() doesn't works for Greenthreads
            thread_name = eventlet.getcurrent().__dict__["greenthread_name"]
        except KeyError:
            # in case the greenthread doesn't have a name set, always provides a value
            thread_name = "unknown?"

        now_console = datetime.now().strftime("%H:%M:%S")
        now_file = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        excess_message_size = len(raw_message) - CONSOLE_LOGGING_LENGTH_CUTOFF

        if cutoff and excess_message_size > 0:
            message = raw_message[:CONSOLE_LOGGING_LENGTH_CUTOFF] + f"... (+ {excess_message_size})"
        else:
            message = raw_message

        if level[0] >= LogLevel.get_level_int(CONSOLE_LOGGING_LEVEL):  # check log level for console logging
            # Greenthreads don't require locks, so this is fine (https://stackoverflow.com/a/2854703/13216113)
            print(f"{level[2]}[{now_console}][{level[1]}][{thread_name}]{Style.RESET_ALL} {message}")
            if exception:
                traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stdout)

        if level[0] >= LogLevel.get_level_int(ERROR_SOUND_NOTIFICATION_LEVEL) \
                and level[1] not in ERROR_SOUND_IGNORE_LEVELS:
            try:
                playsound.playsound(sound=ERROR_SOUND_ABS, block=False)
            except playsound.PlaysoundException as ex:
                Log.trace(f"Sound exception caught: {ex}")

        if ENABLE_FILE_LOGGING and level[0] >= LogLevel.get_level_int(FILE_LOGGING_LEVEL):  # write raw message (and exception) to file if enabled
            Log.FILE_WRITING_QUEUE.put((now_file, level, thread_name, raw_message, exception))

    @staticmethod
    def write_file_loop():
        """Blocking loop to write messages and exceptions to file (from the queue)"""

        set_greenthread_name("LogFileWriter")
        logs_folder_abs = f"{CWD_PATH}/{LOGS_FOLDER}"
        latest_log_abs = f"{logs_folder_abs}/{LATEST_LOG_FILENAME}"

        try:
            open(latest_log_abs, "w").close()
            print(f"Emptied {LATEST_LOG_FILENAME}")

        except FileNotFoundError:
            os.mkdir(logs_folder_abs)
            print(f"Created {logs_folder_abs}")
            open(latest_log_abs, "w").close()
            print(f"Created {LATEST_LOG_FILENAME}")

        Log.trace("Write log file loop ready")

        while True:
            now_str, level, thread_name, message, exception = Log.FILE_WRITING_QUEUE.get()

            with open(latest_log_abs, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}][{level[1]}][{thread_name}] {message}\n")
                if exception:
                    traceback.print_exception(type(exception), exception, exception.__traceback__, file=f)
