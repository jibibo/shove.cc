from convenience import *
from user import User


class GameState:
    IDLE = "idle"
    RUNNING = "running"


class BaseGame(ABC):
    def __init__(self, room):
        self.room = room
        self.events = Queue()
        self.players: List[User] = []
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

            except GameEventInvalid as ex:
                Log.error(f"Event invalid: {ex}")

            except GameEventNotImplemented:
                Log.error("Event not implemented")

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on base_game.handle_event", ex)

            else:
                Log.trace(f"Handled event: '{event}'")

    def get_name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def get_info_packet(self, event: str = None) -> dict:
        pass

    @abstractmethod
    def handle_event(self, event: str):
        pass

    @abstractmethod
    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        pass

    def send_state_packet(self, event: str = None):
        Log.trace(f"Queueing outgoing state packet, event: '{event}'")
        packet = self.get_info_packet(event)
        self.room.send_packet_all("game_state", packet)

    @abstractmethod
    def try_to_start(self):
        """Tries to start the game, throws exception on failure"""
        pass

    @abstractmethod
    def user_left_room(self, user: User):
        pass

    @abstractmethod
    def user_tries_to_join_room(self, user: User):
        """Tries to let user join the room, throws exception on failure"""
        pass
