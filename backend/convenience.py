"""Convenience file for easy imports"""

# builtin modules

from abc import ABC, abstractmethod
from datetime import datetime
import json
import math
import os
import pathlib
import random
import re
import requests  # possibly not greenlet-friendly (builtin IO module)
import secrets
import shutil
import sys
import time
import traceback
from typing import Dict, Iterable, List, Union, Optional, Tuple, Set
import urllib.parse as urlparse


# 3rd-party modules

import colorama
from colorama import Fore, Style
import eventlet
from eventlet.green import subprocess  # greenlet-friendly versions of builtin modules
from eventlet.green.Queue import Queue
import eventlet.wsgi
import isodate
import playsound
import socketio
import trello
import youtube_dl  # possibly not greenlet friendly


# log.Log uses this function, causes NameError if defined later
def set_greenthread_name(name: str):
    """Set the name of the greenthread that called this (for logging)"""

    greenthread = eventlet.getcurrent()
    greenthread.__dict__["greenthread_name"] = name


# local modules

from config import *  # needs to be imported first for CWD_PATH
from exceptions import *
# import formatting  # unused as of now
from log import Log  # shouldn't be a circular import: from x import y shouldn't execute module x


# access private.py (contains sensitive data)
try:
    from private import *
    PRIVATE_ACCESS = True
except ImportError:
    Log.warn("Could not import 'private.py', functions using private information won't work")
    PRIVATE_ACCESS = False


def cleanup_backend_songs_folder():
    """Remove non-mp3 files from backend songs folder"""

    count = 0
    for filename in os.listdir(f"{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}"):
        if not filename.endswith(".mp3"):
            os.remove(f"{BACKEND_DATA_FOLDER}/{SONGS_FOLDER}/{filename}")
            count += 1

    Log.trace(f"Removed {count} file(s) that weren't .mp3 from songs folder")


def empty_frontend_cache():
    """Empty contents of the frontend audio cache folder"""

    count = 0
    for filename in os.listdir(f"{FRONTEND_CACHE_FOLDER}/{SONGS_FOLDER}"):
        os.remove(f"{FRONTEND_CACHE_FOLDER}/{SONGS_FOLDER}/{filename}")
        count += 1

    Log.trace(f"Removed {count} file(s) from frontend cache")


def simulate_intensive_function(seconds):
    """Simulate the time it takes to process input/audio/video/etc."""

    Log.test(f"Simulating intensive function for {seconds} s")
    eventlet.sleep(seconds)
    Log.test(f"Done simulating ({seconds} s)")


def error_packet(description=None) -> dict:
    """Create a default error packet with no useful information whatsoever"""

    return {
        "description": description or DEFAULT_DESCRIPTION
    }


def shlex_quote_windows(s):
    """Custom Windows version of shlex.quote(), replacing single with double quotes.
    Return a shell-escaped version of the string *s*.
    https://superuser.com/q/324278"""

    if not s:
        return "\"\""
    if re.compile(r"[^\w@%+=:,./-]", re.ASCII).search(s) is None:
        return s

    # use DOUBLE quotes, and put DOUBLE quotes into SINGLE quotes
    # the string $'b is then quoted as "$"'"'"b"
    return "\"" + s.replace("\'", "\"\'\"\'\"") + "\""
