from convenience import *
from base_game import BaseGame, InvalidEvent, InvalidGamePacket
from user import User

from .player import Player
from .flip_timer_thread import FlipTimerThread


class Coinflip(BaseGame):
    def __init__(self, room):
        super().__init__(room)
        self.running = False
        self.flip_timer = None
        self.participants: List[Player] = []
        self.winners: Dict[str, int] = {}
        self.flip_timer_left = 0
        self.coin_result = None

        self.flip_timer_duration = 2
        self.heads_odds = 0.5
        self.tails_odds = 0.5

    def handle_event(self, event: str):
        if event == "timer_done":
            self.resolve_flip()
            return

        if event in ["user_bet"]:
            self.try_to_start()
            return

        if event in ["user_joined", "coin_flipped"]:
            Log.warn("not implemented")
            return

        raise InvalidEvent(f"unknown (or incomplete handler for) event: '{event}'")

    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        if model == "game_action":
            action = packet["action"]

            if action == "bet":
                if user in [player.user for player in self.participants]:
                    return "game_action_status", {
                        "success": False,
                        "action": "bet",
                        "reason": "already bet"
                    }

                bet = int(packet["bet"])

                if bet <= 0:
                    return "game_action_status", {
                        "success": False,
                        "action": "bet",
                        "reason": f"invalid bet amount: {bet}"
                    }

                if user.account["money"] < bet:
                    return "game_action_status", {
                        "success": False,
                        "action": "bet",
                        "reason": "not enough money"
                    }

                choice = packet["choice"]
                user.account["money"] -= bet
                self.participants.append(Player(user, choice, bet))
                self.events.put("user_bet")

                return "game_action_status", {
                    "success": True,
                    "action": "bet",
                    "bet": bet,
                    "choice": choice
                }

        if model == "game_state":
            return "game_state", self.get_state_packet()

        raise InvalidGamePacket(f"unknown (or incomplete handler for) game packet model: '{model}'")

    def try_to_start(self) -> Union[None, str]:
        if self.room.is_empty():
            Log.trace("Room is empty, not starting")
            return "room is empty"

        if self.running:
            Log.trace("Game is already running, not starting")
            return "game already running"

        self.flip_timer = FlipTimerThread(self, self.flip_timer_duration)
        self.flip_timer.start()
        self.coin_result = "spinning"
        self.winners.clear()
        self.running = True
        Log.info("Game started!")

        self.send_state_packet(event="started")

    def user_left_room(self, user: User):
        return

    def user_tries_to_join_room(self, user: User) -> Union[None, str]:
        # users can always join room
        return

    def get_state_packet(self, event: str = None) -> dict:
        if self.running or event == "started":
            state = {
                "time_left": self.flip_timer_left,
                "betters": {player.user.account["username"]: player.bet
                            for player in self.participants}
            }

        else:
            state = {
                "winners": self.winners  # the winners of the last coin flip
            }

        return {
            "running": self.running,
            "event": event,
            "state": state,
            "odds": {
                "heads": self.heads_odds,
                "tails": self.tails_odds
            },
            "coin_result": self.coin_result
        }

    def resolve_flip(self):
        Log.trace(f"Resolving flip, odds: heads = {self.heads_odds}, tails = {self.tails_odds})")
        total_odds = self.heads_odds + self.tails_odds
        if random.random() * total_odds < self.heads_odds:  # calculate flip result based on odds
            self.coin_result = "heads"
        else:
            self.coin_result = "tails"

        Log.trace(f"Resolved result: {self.coin_result}")

        for player in self.participants:  # check who won and receives money
            user = player.user
            player_wins = player.choice == self.coin_result
            if player_wins:
                gain = 2 * player.bet
                user.account["money"] += gain
                self.winners[user.account["username"]] = gain

        Log.trace(f"Winners: {self.winners}")

        self.send_state_packet(event="ended")

        self.participants.clear()
        self.running = False

    def send_state_packet(self, user=None, event=None):
        packet = self.get_state_packet(event)

        if user is None:
            self.room.send_packet("game_state", packet)

        else:
            self.room.shove.send_packet(user, "game_state", packet)
