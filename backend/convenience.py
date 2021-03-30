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
    from private import *
    PRIVATE_ACCESS = True
except ImportError:
    Log.error("Could not import 'private.py', functions using private information won't work")
    PRIVATE_ACCESS = False

# this file should be able to be imported by every .py file for convenience
