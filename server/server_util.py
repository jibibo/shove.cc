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


LOG_DEBUG = 0, "DEBUG"
LOG_INFO = 1, "INFO"
LOG_WARN = 2, "WARN"
LOG_ERROR = 3, "ERROR"

LOGGING_LEVEL = LOG_DEBUG
HEADER_SIZE = 10
SERVER_BACKLOG = 5
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12345

PRINT_LOCK = threading.Semaphore(value=1)  # how does this work


def log(message, level=LOG_DEBUG, exception: BaseException=None):
    if level[0] < LOGGING_LEVEL[0]:  # not high enough log level
        return

    thread_name = threading.current_thread().getName()

    PRINT_LOCK.acquire()

    now_str = datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}][{level[1]:<5}][Server/{thread_name}] {message}")

    if exception:
        traceback.print_exception(type(exception), exception, exception.__traceback__)

    PRINT_LOCK.release()
