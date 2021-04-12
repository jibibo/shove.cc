from convenience import *


colorama.init(autoreset=False)


class LogLevel:
    TRACE = 0, "TRACE", ""
    DEBUG = 1, "DEBUG", Fore.CYAN
    INFO = 2, "INFO", Fore.GREEN + Style.BRIGHT
    TEST = 2, "TEST", Fore.MAGENTA
    WARN = 3, "WARN", Fore.YELLOW
    ERROR = 4, "ERROR", Fore.RED
    FATAL = 5, "FATAL", Fore.RED + Style.BRIGHT

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
    FILE_WRITING_QUEUE = Queue()  # now_str, level, thread_name, ex, message, packet

    @staticmethod
    def trace(message, **kwargs):
        Log._log(message, LogLevel.TRACE, **kwargs)

    @staticmethod
    def debug(message, **kwargs):
        Log._log(message, LogLevel.DEBUG, **kwargs)

    @staticmethod
    def info(message, **kwargs):
        Log._log(message, LogLevel.INFO, **kwargs)

    @staticmethod
    def warn(message, **kwargs):
        Log._log(message, LogLevel.WARN, **kwargs)

    @staticmethod
    def error(message, **kwargs):
        Log._log(message, LogLevel.ERROR, **kwargs)

    @staticmethod
    def fatal(message, **kwargs):
        Log._log(message, LogLevel.FATAL, **kwargs)

    @staticmethod
    def test(message, **kwargs):
        Log._log(message, LogLevel.TEST, **kwargs)

    @staticmethod
    def _log(raw_message, level, **kwargs):  # todo filter packet content like bytes
        ex: Exception = kwargs.pop("ex", None)
        cutoff: bool = kwargs.pop("cutoff", True)
        packet = hide_packet_values_for_logging(kwargs.pop("packet", None))
        raw_message = str(raw_message)

        try:
            # dirty way of setting/getting GreenThread names, as threading.current_thread().getName() doesn't works for greenlets
            greenlet_name = eventlet.getcurrent().__dict__["custom_greenlet_name"]
        except KeyError:
            # in case the greenlet doesn't have a name set, always provides a value
            greenlet_name = "UNNAMED GREENLET"

        now_console = datetime.now().strftime("%H:%M:%S")
        now_file = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        excess_message_size = len(raw_message) - CONSOLE_LOGGING_LENGTH_CUTOFF

        if cutoff and excess_message_size > 0:
            message = raw_message[:CONSOLE_LOGGING_LENGTH_CUTOFF] + f"... (+ {excess_message_size})"
        else:
            message = raw_message

        if level[0] >= LogLevel.get_level_int(CONSOLE_LOGGING_LEVEL):  # check log level for console logging
            # Greenthreads don't require locks, so this is fine (https://stackoverflow.com/a/2854703/13216113)
            if packet:
                message += f"\n packet: {packet}"
            print(f"{level[2]}[{now_console}][{level[1]}][{greenlet_name}]{Style.RESET_ALL} {message}")
            if ex:
                traceback.print_exception(type(ex), ex, ex.__traceback__, file=sys.stdout)

        if ERROR_SOUND_ENABLED \
                and level[0] >= LogLevel.get_level_int(ERROR_SOUND_NOTIFICATION_LEVEL) \
                and level[1] not in ERROR_SOUND_IGNORE_LEVELS:
            try:
                playsound.playsound(sound=ERROR_SOUND_FILE_PATH, block=False)
            except playsound.PlaysoundException as ex:
                Log.trace(f"Exception on playsound", ex=ex)

        if ENABLE_FILE_LOGGING and level[0] >= LogLevel.get_level_int(FILE_LOGGING_LEVEL):  # write raw message (and exception) to file if enabled
            Log.FILE_WRITING_QUEUE.put((now_file, level, greenlet_name, raw_message, ex, packet))

    @staticmethod
    def write_file_loop():
        """Blocking loop to write messages and exceptions to file (from the queue)"""

        set_greenlet_name("LogFileWriter")
        latest_log_abs = f"{LOGS_FOLDER}/{LATEST_LOG_FILENAME}"

        try:
            open(latest_log_abs, "w").close()
            print(f"Emptied {LATEST_LOG_FILENAME}")

        except FileNotFoundError:
            os.mkdir(LOGS_FOLDER)
            print(f"Created {LOGS_FOLDER}")
            open(latest_log_abs, "w").close()
            print(f"Created {LATEST_LOG_FILENAME}")

        Log.trace("Write log file loop ready")

        while True:
            now_str, level, thread_name, message, ex, packet = Log.FILE_WRITING_QUEUE.get()
            if packet:
                message += f"\n packet: {packet}"

            with open(latest_log_abs, "a") as f:
                f.write(f"[{now_str}][{level[1]}][{thread_name}] {message}\n")
                if ex:
                    traceback.print_exception(type(ex), ex, ex.__traceback__, file=f)


def hide_packet_values_for_logging(packet: Union[dict, list]) -> Optional[Union[dict, list]]:
    """Recursively hide values in packet containing useless info (like entire files) from being logged"""

    if not packet:
        return packet

    packet_copy = packet.copy()

    if type(packet) == list:
        return [hide_packet_values_for_logging(element) for element in packet_copy]

    if type(packet) == dict:
        for key in packet_copy:
            if key in HIDE_PACKET_KEYS:
                packet_copy[key] = "<hidden>"
            elif key in ABBREVIATE_NUMBER_KEYS:
                packet_copy[key] = abbreviate(packet_copy[key])

        return packet_copy

    raise ValueError(f"Unsupported type: {type(packet).__name__}")


abbreviations = ["", "K", "M", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No"]


def abbreviate(number: int) -> str:
    """
    Return a human-readable string of the given number. Supported range: [0, 1e32]
    Should usually just be done by the frontend, saves a lot of packets
    todo test on negative numbers, also in frontend JS version
    """

    try:
        number = int(number)
    except ValueError:
        return "<NaN>"

    if number == 0:
        return "<0>"

    magnitude = int(math.floor((math.log10(number))))

    if magnitude < 3:  # number too small
        return str(number)

    new_number = number / 10 ** magnitude

    if new_number >= 9.995:  # possible carry-over that turns rounding into n >= 10 instead of [1, 9.99]
        magnitude += 1
        new_number /= 10

    magnitude_remainder = magnitude % 3
    decimals = None if (magnitude_remainder == 2 or magnitude < 3) else 2 - magnitude_remainder  # what
    new_number *= 10 ** magnitude_remainder
    new_number = round(new_number, decimals)

    abbreviation_index = int(magnitude / 3)
    abbreviation = abbreviations[abbreviation_index]
    abbreviated_number = str(new_number) + abbreviation

    # Log.test(f"Abbreviated {number} to {abbreviated_number}")
    return f"<{abbreviated_number}>"
