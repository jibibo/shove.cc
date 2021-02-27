import socket
import time
import json
import os
import traceback
import threading
import sys
import random
from queue import Queue
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List
import colorama
from colorama import Fore, Style

colorama.init(autoreset=False)


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
    LEVEL_TRACE = 0, "TRACE", Fore.WHITE
    LEVEL_DEBUG = 1, "DEBUG", Fore.CYAN
    LEVEL_INFO = 2, "INFO", Fore.GREEN
    LEVEL_WARN = 3, "WARN", Fore.YELLOW
    LEVEL_ERROR = 4, "ERROR", Fore.RED
    LEVEL_FATAL = 5, "FATAL", Fore.RED + Style.BRIGHT
    LEVEL_TEST = 6, "TEST", Fore.MAGENTA

    PRINT_LOCK = threading.Semaphore(value=1)  # how does this work

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
        if level[0] < CONSOLE_LOG_LEVEL[0]:  # not high enough log level
            return

        thread_name = threading.current_thread().getName()
        now_str = datetime.now().strftime("%H:%M:%S")

        Log.PRINT_LOCK.acquire()
        print(f"[{now_str}]{level[2]}[S/{level[1]:<5}]{Style.RESET_ALL}[{thread_name}] {message}")

        if exception:
            print(f"{Log.LEVEL_FATAL[2]}", end="")
            traceback.print_exception(type(exception), exception, exception.__traceback__)
            print(f"{Style.RESET_ALL}", end="")

        Log.PRINT_LOCK.release()


CONSOLE_LOG_LEVEL = Log.LEVEL_TRACE
HEADER_SIZE = 10
SERVER_BACKLOG = 5
SERVER_PORT = 12345
