import socket
import time
import json
import os
import threading
from queue import Queue
from datetime import datetime


class LostConnection(BaseException):
    def __init__(self, reason):
        self.reason = reason


class StopServer(BaseException):
    pass


class UnknownPacketModel(BaseException):
    pass


class LogLevel:
    DEBUG = 0, "DEBUG"
    INFO = 1, "INFO"
    WARN = 2, "WARN"
    ERROR = 3, "ERROR"


LOGGING_LEVEL = LogLevel.DEBUG
HEADER_SIZE = 10
SERVER_BACKLOG = 5
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12345

PRINT_LOCK = threading.Semaphore(value=1)  # how does this work


def log(message, level=LogLevel.DEBUG):
    if level[0] < LOGGING_LEVEL[0]:  # not high enough log level
        return

    thread_name = threading.current_thread().getName()

    PRINT_LOCK.acquire()
    now_str = datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}][{level[1]:<5}][Server/{thread_name}] {message}")
    PRINT_LOCK.release()
