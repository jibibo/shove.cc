from convenience import *
from user import User


class GameState:
    IDLE = "idle"
    RUNNING = "running"
    ENDED = "ended"


class BaseGame(ABC):
    def __init__(self, room):
        self.room = room
        self.events = Queue()
        self.players: List[User] = []
        self.state = GameState.IDLE
        threading.Thread(target=self._event_handler_thread,
                         name=f"EHand/{self.room.name}",
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

    @abstractmethod
    def get_data(self, event: str = None) -> dict:
        pass

    def get_name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def handle_event(self, event: str):
        pass

    @abstractmethod
    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        pass

    def send_data_packet(self, event: str = None):
        Log.trace(f"Queueing game data packet for all users, event: '{event}'")
        packet = self.get_data(event)
        self.room.send_packet_all("game_data", packet)

    @abstractmethod
    def try_to_start(self):
        """Tries to start the game, throws exception on failure"""
        pass

    @abstractmethod
    def user_leaves_room(self, user: User):
        """Called when user leaves a room (can't be prevented)"""
        pass

    @abstractmethod
    def user_tries_to_join_room(self, user: User):
        """Tries to let user join the room, throws exception on failure"""
        pass
