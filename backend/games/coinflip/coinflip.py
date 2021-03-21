from convenience import *
from base_game import BaseGame, InvalidEvent, InvalidGamePacket, GameState
from user import User

from .flip_timer_thread import FlipTimerThread


class Player:
    def __init__(self, user, choice, bet):
        self.user = user
        self.choice = choice
        self.bet = bet


class Coinflip(BaseGame):
    def __init__(self, room):
        super().__init__(room)
        self.flip_timer = None
        self.participants: List[Player] = []
        self.winners: Dict[str, int] = {}
        self.coin_state = None

        self.flip_timer_duration = 2
        self.heads_odds = 49  # 49/total odds = 49%
        self.tails_odds = 51  # 51/total odds = 51%

    def handle_event(self, event: str):
        if event == "timer_finished":
            self.resolve_flip()
            return

        if event == "timer_ticked":
            self.send_state_packet(event="timer_ticked")
            return

        if event == "user_bet":
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
            return "Room is empty"

        if self.state == GameState.RUNNING:
            Log.trace("Game is already running, not starting")
            return "Game is already running"

        self.state = GameState.RUNNING
        self.winners.clear()
        self.coin_state = "spinning"
        self.flip_timer = FlipTimerThread(self, self.flip_timer_duration)
        self.flip_timer.start()

        Log.info("Game started")
        self.send_state_packet(event="started")

    def user_left_room(self, user: User):
        return

    def user_tries_to_join_room(self, user: User) -> Union[None, str]:
        # users can always join room in this game
        return

    def get_state_packet(self, event: str = None) -> dict:  # todo should probably be in BaseGame
        if self.state == GameState.IDLE:
            info = {
                "winners": self.winners  # the winners of the last coin flip
            }

        else:  # self.state == GameState.RUNNING
            info = {
                "time_left": self.flip_timer.time_left,
                "betters": {player.user.account["username"]: player.bet
                            for player in self.participants}
            }

        return {
            "state": self.state,
            "event": event,
            "info": info,
            "odds": {
                "heads": self.heads_odds,
                "tails": self.tails_odds
            },
            "coin_state": self.coin_state
        }

    def resolve_flip(self):
        Log.trace(f"Resolving flip (odds: heads = {self.heads_odds}, tails = {self.tails_odds})")
        total_odds = self.heads_odds + self.tails_odds
        if random.random() * total_odds < self.heads_odds:  # calculate flip result based on odds
            self.coin_state = "heads"
        else:
            self.coin_state = "tails"

        Log.trace(f"Resolved result: {self.coin_state}")

        for player in self.participants:  # check who won and receives money
            user = player.user
            player_wins = player.choice == self.coin_state
            if player_wins:
                gain = 2 * player.bet
                user.account["money"] += gain
                self.winners[user.account["username"]] = gain

        Log.trace(f"Winners: {self.winners}")
        self.state = GameState.IDLE
        self.participants.clear()

        self.send_state_packet(event="ended")

    def send_state_packet(self, event: str = None):  # todo should probably be in BaseGame
        Log.trace(f"Queueing outgoing state packet, event: '{event}'")
        packet = self.get_state_packet(event)
        self.room.send_packet("game_state", packet)
