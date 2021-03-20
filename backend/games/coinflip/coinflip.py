from convenience import *
from base_game import BaseGame, InvalidEvent, InvalidGamePacket
from user import User

from .player import Player


class Coinflip(BaseGame):
    def __init__(self, room):
        super().__init__(room)
        self.running = False
        self.flip_timer = None
        self.participants: List[Player] = []
        self.flip_timer_duration = 10
        self.flip_timer_left = 0
        self.heads_odds = 0.1
        self.tails_odds = 0.9

    def handle_event(self, event: str):
        if event == "timer_done":
            self.flip_coin()
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
                if self.user_has_already_bet(user):
                    return "game_action_status", {
                        "success": False,
                        "action": "bet",
                        "reason": "already bet"
                    }

                bet = int(packet["bet"])

                if not bet:
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

        raise InvalidGamePacket(f"unknown (or incomplete handler for) game packet model: '{model}'")

    def try_to_start(self) -> Union[None, str]:
        if self.room.is_empty():
            Log.trace("Room is empty, not starting")
            return "room is empty"

        if self.running:
            Log.trace("Game is already running, not starting")
            return "game already running"

        self.flip_timer = threading.Thread(target=self.flip_timer_thread,
                                           name=f"{self.room.name}/FlipTimer",
                                           daemon=True)
        self.flip_timer.start()

        self.running = True
        Log.info("Game started!")

    def user_left_room(self, user: User):
        pass

    def user_tries_to_join_room(self, user: User) -> Union[None, str]:
        # self.events.put("user_joined")
        self.send_state_packet(user)
        return

    def flip_coin(self):
        Log.trace(f"Flipping coin, odds: heads = {self.heads_odds}, tails = {self.tails_odds})")
        total_odds = self.heads_odds + self.tails_odds
        if random.random() * total_odds < self.heads_odds:
            result = "heads"
        else:
            result = "tails"

        Log.trace(f"Result: {result}")

        winners = {}
        for player in self.participants:  # notify each participant of their win/loss
            user = player.user
            player_wins = player.choice == result
            if player_wins:
                gain = 2 * player.bet
                user.account["money"] += gain
                winners[user.account["username"]] = gain

        Log.trace(f"Winners: {winners}")

        self.room.send_packet("game_ended", {
            "result": result,
            "winners": winners
        })

        self.participants.clear()
        self.running = False
        # self.events.put("coin_flipped")

    def flip_timer_thread(self):
        self.flip_timer_left = self.flip_timer_duration
        Log.trace(f"Flip timer started, duration: {self.flip_timer_duration}")
        self.room.send_packet("game_started", self.get_state_packet()[1])

        while self.flip_timer_left:
            time.sleep(1)
            self.flip_timer_left -= 1
            if self.flip_timer_left:
                self.send_state_packet()

        Log.trace("Timer done")
        self.events.put("timer_done")

    def get_state_packet(self) -> Tuple[str, dict]:
        return "game_state", {
            "time_left": self.flip_timer_left,
            "betters": {player.user.account["username"]: player.bet
                        for player in self.participants}
        }

    def send_state_packet(self, user=None):
        model, packet = self.get_state_packet()

        if user is None:
            self.room.send_packet(model, packet)

        else:
            self.room.shove.send_packet(user, model, packet)

    def user_has_already_bet(self, user) -> bool:
        for player in self.participants:
            if player.user == user:
                return True

        return False