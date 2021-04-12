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
import requests  # possibly not greenlet-friendly
import secrets
import shutil
import sys
import time
import traceback
from typing import Dict, Iterable, List, Union, Optional, Tuple, Set
import urllib.parse as urlparse
import uuid


# 3rd-party modules

import colorama
from colorama import Fore, Style
import eventlet
from eventlet.green import subprocess  # greenlet-friendly versions of builtin modules
from eventlet.green.Queue import Queue
import eventlet.wsgi
import socketio
import isodate
import playsound
import trello
import youtube_dl  # possibly not greenlet friendly


# log.Log uses this function, causes NameError if defined later
def set_greenlet_name(name: str):
    """Set the name of the greenlet that called this (for logging)"""

    greenlet = eventlet.getcurrent()
    greenlet.__dict__["custom_greenlet_name"] = name


# local modules

from config import *
from exceptions import *
# import formatting  # unused as of now
from log import Log, abbreviate  # shouldn't be a circular import; from x import y shouldn't execute module x


# access private.py (contains sensitive data)
try:
    from top_secret_private_keys import *
    PRIVATE_KEYS_IMPORTED = True
except ImportError:
    Log.warn("Could not import 'top_secret_private_keys.py', functions using private keys won't work!")
    PRIVATE_KEYS_IMPORTED = False


def cleanup_backend_songs_folder():
    """Remove non-mp3 files from backend songs folder"""

    count = 0
    for filename in os.listdir(f"{FILES_FOLDER}/{SONGS_FOLDER}"):
        if not filename.endswith(".mp3"):
            os.remove(f"{FILES_FOLDER}/{SONGS_FOLDER}/{filename}")
            count += 1

    Log.trace(f"Removed {count} file(s) that weren't .mp3 from songs folder")


def simulate_intensive_function(seconds):
    """Simulate the time it takes to process input/audio/video/etc."""

    Log.test(f"Simulating intensive function for {seconds} s")
    time.sleep(seconds)
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
