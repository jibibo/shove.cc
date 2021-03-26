import time
import json
import os
import sys
import threading
import secrets
import random
import math
from queue import Queue
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Union, Optional, Tuple, Set

from trello import TrelloClient
import playsound
import pathlib

from log import Log
from exceptions import *
import formatting

try:
    from test import TRELLO_API_KEY, TRELLO_API_SECRET, TRELLO_TOKEN
except ImportError:
    Log.error("Could not import Trello API credentials")
    API_KEY = API_SECRET = TOKEN = None

# this file should be able to be imported by every .py file for convenience
