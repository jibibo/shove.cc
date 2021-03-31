import time
import json
import os
import sys
import threading
import secrets
import random
import math
import pathlib
import re
import requests
import multiprocessing
import shutil
from queue import Queue
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Union, Optional, Tuple, Set

from trello import TrelloClient
import playsound
import googleapiclient
import youtube_dl

# needs to be defined before importing the rest of the modules
CWD_PATH = os.path.abspath(os.getcwd()).replace("\\", "/")

from exceptions import *
import formatting
from log import Log  # circular import reference, might go wrong who knows

try:
    from private import *
    PRIVATE_ACCESS = True
except ImportError:
    Log.error("Could not import 'private.py', functions using private information won't work")
    PRIVATE_ACCESS = False

# this file should be able to be imported by every .py file for convenience
