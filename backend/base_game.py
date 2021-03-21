from convenience import *
from user import User


class GameState:
    IDLE = "idle"
    RUNNING = "running"


class InvalidEvent(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class InvalidGamePacket(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class BaseGame(ABC):
    def __init__(self, room):
        self.room = room
        self.events = Queue()
        self.state = GameState.IDLE
        threading.Thread(target=self._event_handler_thread,
                         name=f"{self.room.name}/EventHandler",
                         daemon=True).start()
        Log.trace(f"Game '{type(self).__name__}' initialized for room {room}")

    def _event_handler_thread(self):
        Log.trace("Ready")

        while True:
            event = self.events.get()
            Log.debug(f"Handling event: '{event}'")

            try:
                self.handle_event(event)

            except InvalidEvent as ex:
                Log.error(f"Invalid event: {ex}")
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on self.handle_event", ex)
                continue

            Log.trace(f"Handled event: '{event}'")

    @abstractmethod
    def handle_event(self, event: str):
        return

    @abstractmethod
    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        return

    @abstractmethod
    def try_to_start(self) -> Union[None, str]:
        """Returns a reason if start is denied by ongoing game, otherwise None"""
        return

    @abstractmethod
    def user_left_room(self, user: User):
        return

    @abstractmethod
    def user_tries_to_join_room(self, user: User) -> Union[None, str]:
        """Returns a reason if user join is denied by ongoing game, otherwise None"""
        return
