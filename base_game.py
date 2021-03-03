from util import *


class BaseGame(ABC):
    def __init__(self, table):
        self.table = table
        self.players = []
        self.running = False

    @abstractmethod
    def handle_event(self, event: str):
        pass

    @abstractmethod
    def start(self):
        pass
