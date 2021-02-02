import socket
import time
import json
import sys
import threading
from queue import Queue
from datetime import datetime


class Exit(BaseException):
    pass


class LostConnection(BaseException):
    def __init__(self, reason):
        self.reason = reason


class UnknownPacketModel(BaseException):
    pass


class LogLevel:
    DEBUG = 0, "DEBUG"
    INFO = 1, "INFO"
    WARN = 2, "WARN"
    ERROR = 3, "ERROR"


CONNECT_ATTEMPTS = 3
LOGGING_LEVEL = LogLevel.DEBUG
HEADER_SIZE = 10
SERVER_BACKLOG = 5
SERVER_ADDRESS = "127.0.0.1", 12345

PRINT_LOCK = threading.Semaphore(value=1)  # how does this work


def log(message, level=LogLevel.DEBUG):
    if level[0] < LOGGING_LEVEL[0]:  # not high enough log level
        return

    thread_name = threading.current_thread().getName()
    now_str = datetime.now().strftime("%H:%M:%S")

    PRINT_LOCK.acquire()
    print(f"[{now_str}][{level[1]:<5}][Client/{thread_name}] {message}")
    PRINT_LOCK.release()
