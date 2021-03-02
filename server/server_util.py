import socket
import time
import json
import os
import traceback
import threading
import sys
import random
import secrets
import itertools
from queue import Queue
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List
import colorama
from colorama import Fore, Style


class InvalidPacket(Exception):
    def __init__(self, details):
        self.details = str(details)

    def __str__(self):
        return self.details


class LostConnection(Exception):
    def __init__(self, reason):
        self.reason = reason


class StopServer(Exception):
    pass


class Log:  # todo writing to file
    LEVEL_TRACE = 0, "TRACE", ""
    LEVEL_DEBUG = 1, "DEBUG", Fore.CYAN
    LEVEL_INFO = 2, "INFO", Fore.GREEN + Style.BRIGHT
    LEVEL_WARN = 3, "WARN", Fore.YELLOW
    LEVEL_ERROR = 4, "ERROR", Fore.RED
    LEVEL_FATAL = 5, "FATAL", Fore.RED + Style.BRIGHT
    LEVEL_TEST = 6, "TEST", Fore.MAGENTA

    PRINT_LOCK = threading.Lock()

    WRITING_QUEUE = Queue()

    @staticmethod
    def trace(message, exception=None):
        Log.log(message, level=Log.LEVEL_TRACE, exception=exception)

    @staticmethod
    def debug(message, exception=None):
        Log.log(message, level=Log.LEVEL_DEBUG, exception=exception)

    @staticmethod
    def info(message, exception=None):
        Log.log(message, level=Log.LEVEL_INFO, exception=exception)

    @staticmethod
    def warn(message, exception=None):
        Log.log(message, level=Log.LEVEL_WARN, exception=exception)

    @staticmethod
    def error(message, exception=None):
        Log.log(message, level=Log.LEVEL_ERROR, exception=exception)

    @staticmethod
    def fatal(message, exception=None):
        Log.log(message, level=Log.LEVEL_FATAL, exception=exception)

    @staticmethod
    def test(message, exception=None):
        Log.log(message, level=Log.LEVEL_TEST, exception=exception)

    @staticmethod
    def log(message, level, exception=None):

        thread_name = threading.current_thread().getName()
        now_str = datetime.now().strftime("%H:%M:%S")

        Log.WRITING_QUEUE.put((now_str, level, thread_name, message))

        if level[0] < CONSOLE_LOG_LEVEL[0]:  # not high enough log level
            return

        Log.PRINT_LOCK.acquire()
        print(f"[{now_str}]{level[2]}[SERVER/{level[1]:<5}]{Style.RESET_ALL}[{thread_name}] {message}")

        if exception:
            print(f"{Log.LEVEL_FATAL[2]}", end="")
            traceback.print_exception(type(exception), exception, exception.__traceback__)
            print(f"{Style.RESET_ALL}", end="")

        Log.PRINT_LOCK.release()

    @staticmethod
    def start_log_writing_thread():
        threading.Thread(target=Log.write_to_log_file_thread, name="LogWriter", daemon=True).start()

    @staticmethod
    def write_to_log_file_thread():
        while True:
            now_str, level, thread_name, message = Log.WRITING_QUEUE.get()

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}][SERVER/{level[1]:<5}][{thread_name}] {message}\n")


CONSOLE_LOG_LEVEL = Log.LEVEL_TRACE
LOG_FILE = "logs/_latest.log"
HEADER_SIZE = 10
SERVER_BACKLOG = 5
SERVER_PORT = 12345

colorama.init(autoreset=False)
try:
    open(LOG_FILE, "w").close()
except FileNotFoundError:
    os.mkdir("logs")
    open(LOG_FILE, "w").close()