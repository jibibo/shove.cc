import time
import json
import os
import sys
import threading
import secrets
import random
from queue import Queue
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Union, Optional


class InvalidPacket(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
