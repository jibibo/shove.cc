from convenience import *
from base_game import BaseGame, GameState
from user import User

from .flip_timer_thread import FlipTimerThread


class Coinflip(BaseGame):
    def __init__(self, room):
        super().__init__(room)
        self.flip_timer = None
        self.winners: Dict[str, int] = {}
        self.coin_state = None

        self.flip_timer_duration = 2
        self.heads_odds = 49  # ratio (vs tails) of landing on heads
        self.tails_odds = 51

    def get_info_packet(self, event: str = None) -> dict:
        if self.state == GameState.IDLE:
            info = {
                "winners": self.winners  # the winners of the last coin flip
            }

        else:  # self.state == GameState.RUNNING
            info = {
                "time_left": self.flip_timer.time_left,
                "betters": {player.account["username"]: player.game_data["bet"]
                            for player in self.players}
            }

        info["odds"] = {
            "heads": self.heads_odds,
            "tails": self.tails_odds
        }
        info["coin_state"] = self.coin_state

        return {
            "name": self.get_name(),
            "state": self.state,
            "event": event,
            "info": info,
        }

    def handle_event(self, event: str):
        if event == "timer_finished":
            self.resolve_flip()
            return

        if event == "timer_ticked":
            self.send_state_packet(event="timer_ticked")
            return

        if event == "user_bet":
            try:
                self.try_to_start()

            except GameStartError as ex:
                Log.trace(f"Could not start game: {ex}")

            return

        if event in ["user_joined", "coin_flipped"]:
            raise GameEventNotImplemented

        raise GameEventInvalid(f"Unknown event: '{event}'")

    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        if model == "try_game_action":
            action = packet["action"]

            if action != "bet":
                raise PacketInvalid("Invalid action")

            if user in self.players:
                raise GameActionFailed("Already placed a bet")

            bet = int(packet["bet"])

            if bet <= 0:
                raise GameActionFailed(f"Invalid bet amount: {bet}")

            if user.account["money"] < bet:
                raise GameActionFailed("Not enough money to bet")

            choice = packet["choice"]
            user.account["money"] -= bet
            user.game_data = {
                "choice": choice,
                "bet": bet
            }
            self.players.append(user)
            self.events.put("user_bet")

            return "game_action_success", {
                "action": "bet",
                "bet": bet,
                "choice": choice
            }

        raise PacketInvalid(f"Unknown game packet model: '{model}'")

    def try_to_start(self):
        if self.room.is_empty():
            raise RoomEmpty

        if self.state == GameState.RUNNING:
            raise GameRunning

        self.state = GameState.RUNNING
        self.winners.clear()
        self.coin_state = "spinning"
        self.flip_timer = FlipTimerThread(self, self.flip_timer_duration)
        self.flip_timer.start()

        Log.info("Game started")
        self.send_state_packet(event="started")

    def user_left_room(self, user: User):
        pass

    def user_tries_to_join_room(self, user: User):
        # users can always join room in this game
        pass

    def resolve_flip(self):
        Log.trace(f"Resolving flip (odds: heads = {self.heads_odds}, tails = {self.tails_odds})")
        total_odds = self.heads_odds + self.tails_odds
        if random.random() * total_odds < self.heads_odds:  # calculate flip result based on odds
            self.coin_state = "heads"
        else:
            self.coin_state = "tails"

        Log.trace(f"Resolved result: {self.coin_state}")

        for player in self.players:  # check who won and receives money
            player_wins = player.game_data["choice"] == self.coin_state
            if player_wins:
                gain = 2 * player.game_data["bet"]
                player.account["money"] += gain
                self.winners[player.account["username"]] = gain

        Log.trace(f"Winners: {self.winners}")

        # todo these 3 operations could be in BaseGame.game_ended() or something
        self.state = GameState.IDLE
        self.players.clear()
        self.send_state_packet(event="ended")
