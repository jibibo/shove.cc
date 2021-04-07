"""This file should be able to be imported by every local .py file for convenience"""

# builtin modules

import time
import json
import os
import sys
import threading  # use green variant!?
import secrets
import random
import math
import pathlib
import re
import requests
import shutil
import urllib.parse as urlparse
import traceback
from queue import Queue
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Union, Optional, Tuple, Set


# 3rd-party modules

import eventlet
import eventlet.wsgi
from eventlet.green import subprocess  # https://stackoverflow.com/a/34649180/13216113
# from eventlet.green import threading
from trello import TrelloClient
import playsound
import socketio
from mutagen.mp3 import MP3
import colorama
from colorama import Fore, Style
# import googleapiclient
# import youtube_dl


# these need to be defined before importing local modules

CWD_PATH = os.path.abspath(os.getcwd()).replace("\\", "/")  # used by many local modules


def set_greenthread_name(name: str):  # log.Log uses this function, causes NameError if defined later
    """Set the name of the greenthread that called this (for logging)"""

    greenthread = eventlet.getcurrent()
    greenthread.__dict__["greenthread_name"] = name


# local modules

from config import *  # needs to be imported first for CWD_PATH
from exceptions import *
import formatting
from log import Log  # shouldn't be a circular import: from x import y shouldn't execute module x


# access private.py (contains sensitive data)
try:
    from private import *
    PRIVATE_ACCESS = True
except ImportError:
    Log.warn("Could not import 'private.py', functions using private information won't work")
    PRIVATE_ACCESS = False


def cleanup_backend_youtube_cache():
    """Remove non-mp3 files from backend youtube cache folder"""

    count = 0
    for filename in os.listdir(f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}"):
        if not (filename.endswith(".mp3") or filename.endswith(".txt")):
            os.remove(f"{CWD_PATH}/{BACKEND_AUDIO_CACHE}/{filename}")
            count += 1

    Log.trace(f"Removed {count} file(s) that weren't .mp3 or .txt from backend/youtube_cache")


def empty_frontend_cache():
    """Empty contents of the frontend audio cache folder"""

    count = 0
    for filename in os.listdir(f"{CWD_PATH}/{FRONTEND_AUDIO_CACHE}"):
        os.remove(f"{CWD_PATH}/{FRONTEND_AUDIO_CACHE}/{filename}")
        count += 1

    Log.trace(f"Removed {count} file(s) in frontend/audio")


def simulate_intensive_function(seconds):
    """Simulate the time it takes to process input/audio/video/etc."""

    Log.test(f"Simulating intensive function for {seconds} s")
    eventlet.sleep(seconds)
    Log.test(f"Done simulating ({seconds} s)")


def default_error_packet(error=None, description=None) -> dict:
    """Create a default error packet with no useful information whatsoever"""

    return {
        "error": error or DEFAULT_ERROR,
        "description": description or DEFAULT_DESCRIPTION
    }
