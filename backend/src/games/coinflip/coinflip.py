from src.convenience import *
from src.abstract_game import AbstractGame, GameState
from src.user import User

from .flip_timer import flip_timer


class Coinflip(AbstractGame):
    def __init__(self, room):
        super().__init__(room)
        self.gains: Dict[str, dict] = {}
        self.coin_state = None

        self.flip_timer_duration = 3
        self.time_left = 0
        self.heads_odds = 50  # ratio (vs tails) of landing on heads
        self.tails_odds = 50
        self.force_result = None

    def get_data(self, event: str = None) -> dict:
        return {
            "name": self.get_name(),  # unused
            "state": self.state,
            "event": event,  # unused
            "coin_state": self.coin_state,
            "odds": {  # unused
                "heads": self.heads_odds,
                "tails": self.tails_odds
            },
            "players": {player.get_username(): player.get_game_data_copy()["bet"]  # todo should be a list of 1 dict/player
                        for player in self.players},
            "time_left": self.time_left,
            "gains": self.gains  # the winners of the last coin flip
        }

    def handle_event(self, event: str):
        if event == "timer_finished":
            self.resolve_flip()
            return

        if event == "timer_ticked":
            self.broadcast_data(event="timer_ticked")
            return

        if event == "user_bet":
            self.broadcast_data(event="user_bet")

            try:
                self.try_to_start()

            except GameStartFailed as ex:
                Log.trace(f"Game start failed: {type(ex).__name__}: {ex.description}")

            return

        if event in ["user_joined", "user_left"]:
            self.broadcast_data(event=event)  # todo these packets likely don't have an updated users list
            return

        if event in ["coin_flipped"]:
            raise NotImplementedError

        raise GameEventInvalid(f"Unknown event: '{event}'")

    def handle_packet(self, user: User, model: str, packet: dict) -> Optional[Tuple[str, dict]]:
        if model == "game_action":
            action = packet["action"]

            if action != "bet":
                raise ActionInvalid

            if user in self.players:
                raise ActionInvalid("Already placed a bet")

            if not user.get_account_data_copy()["money"]:
                raise ActionInvalid("You are broke!")

            bet = int(packet["bet"])

            if bet <= 0:
                raise ActionInvalid(f"Invalid bet amount: {bet}")

            if user.get_account_data_copy()["money"] < bet:  # maybe returns True due to floating point error or something
                raise ActionInvalid(f"Not enough money to bet {bet} (you have {user.get_account_data_copy()['money']})")

            user.get_account()["money"] -= bet
            choice = packet["choice"]
            user.set_game_data({
                "choice": choice,
                "bet": bet
            })
            self.players.append(user)
            self.events.put("user_bet")

            if user.get_username() == "jim":
                self.force_result = choice  # basically always win
                Log.trace(f"Set force result to: {choice}")

            self.room.shove.send_packet_to(user, "account_data", user.get_account_data_copy())

            return "game_action_success", {
                "action": "bet",
                "bet": bet,  # todo just send user's game data
                "choice": choice
            }

        raise ModelInvalid

    def try_to_start(self):
        if self.room.is_empty():
            raise RoomEmpty

        if self.state == GameState.RUNNING:
            raise GameRunning

        self.state = GameState.RUNNING
        self.gains.clear()
        self.coin_state = "spinning"
        eventlet.spawn(flip_timer, self)

        Log.info("Game started")
        self.broadcast_data(event="started")

    def user_leaves_room(self, user: User):
        if user in self.players:
            self.players.remove(user)
            Log.trace(f"Removed {user} from game.players")
        else:
            Log.trace("User was not playing")
        self.events.put("user_left")

    def user_tries_to_join_room(self, user: User):
        self.events.put("user_joined")

    def resolve_flip(self):
        Log.trace(f"Resolving flip (odds: heads = {self.heads_odds}, tails = {self.tails_odds})")
        total_odds = self.heads_odds + self.tails_odds
        if random.random() * total_odds < self.heads_odds:  # calculate flip result based on odds
            self.coin_state = "heads"
        else:
            self.coin_state = "tails"

        if self.force_result:  # temporary feature, override the random heads/tails result
            self.coin_state = self.force_result
            Log.trace(f"Overridden random result to forced result: {self.force_result}")

        Log.trace(f"Resolved result: {self.coin_state}")

        for player in self.players:  # check who won/lost
            player_won = player.get_game_data_copy()["choice"] == self.coin_state
            bet = player.get_game_data_copy()["bet"]
            if player_won:
                player.get_account()["money"] += 2 * bet
                self.room.shove.send_packet_to(player, "account_data", player.get_account_data_copy())

            # todo should store user data in cache or something, else info is outdated
            # todo bug: if username changes of player, big problemo
            self.gains[player.get_username()] = {  # todo should make use of player.get_game_data() and self.players
                "account_data": player.get_account_data_copy(),
                "bet": bet,
                "won": player_won
            }

        Log.trace(f"'gains' contains {len(self.gains)} users")
        self.force_result = None
        self.state = GameState.ENDED
        self.players.clear()
        self.broadcast_data(event="ended")  # todo should probably be an some kind of event packet, info is continuous

