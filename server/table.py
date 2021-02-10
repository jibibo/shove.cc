from util_server import *
from player import Player
from table_handler import TableHandler
from deuces_custom.deck import Deck


class Table:
    MIN_PLAYERS = 2

    def __init__(self, server, name, seats=10):
        self.server = server
        self.name = name

        self.dealer_seat = 0  # not set
        self.small_blind_seat = 0
        self.big_blind_seat = 0
        self.action_seat = 0

        self.deck = Deck()
        self.seats_players = {}
        self.events = Queue()
        self.event_handler = TableHandler(self)
        self.game_over = False
        self.state = STATE_WAITING

        self.event_handler.start()

        for i in range(1, seats + 1):
            self.seats_players[i] = None

        log(f"Created table {self}", LOG_INFO)

    def __repr__(self):
        return f"'{self.name}' with {self.n_taken_seats()}/{self.n_total_seats()} players"

    def action_on_next_player(self):
        pass

    def add_bot(self, seat=None) -> int:
        return self.add_player(Player.create_bot(), seat)

    def add_bots(self, amount=1):
        added_bots = 0

        for _ in range(amount):
            if self.add_bot():
                added_bots += 1

        log(f"Added {added_bots}/{amount} bots")

    def add_player(self, player, seat=None) -> int:  # returns set seat
        if self.state == STATE_STARTED:
            log("Game already started")  # todo add to a queue to join next round
            return 0

        assert player, "no player given"

        empty_seats = self.get_empty_seats()

        if not empty_seats:
            log("No seats empty, ignoring call", LOG_WARN)
            return 0

        if seat:
            if seat in empty_seats:
                log(f"Given seat {seat} is available")
            else:
                log(f"Given seat {seat} is taken, choosing random seat", LOG_WARN)
                seat = random.choice(empty_seats)

        else:
            log(f"No seat given, choosing random seat")
            seat = random.choice(empty_seats)

        self.seats_players[seat] = player
        log(f"Put player {player['username']} in seat {seat}", LOG_INFO)
        self.events.put("player_added")
        return seat

    def attempt_start(self):
        log(f"Attempting to start...")

        if not self.attempt_update_state(STATE_STARTED):
            return

        if self.n_taken_seats() >= Table.MIN_PLAYERS:
            self.on_start()

    def attempt_update_state(self, new_state) -> bool:
        log("Attempting to update state...")

        if (self.state == STATE_WAITING and new_state == STATE_STARTED) or \
                (self.state == STATE_STARTED and new_state == STATE_ENDING) or \
                (self.state == STATE_ENDING and new_state == STATE_WAITING):
            old = self.state
            self.state = new_state
            log(f"Updated state from {old} to {new_state}")
            return True

        log(f"Can't update state to {new_state} (currently: {self.state})")
        return False

    def check_game_over(self) -> bool:
        return bool(self.game_over)

    def deal_player_cards(self):
        log("Dealing cards to players...")

        for seat, player in self.get_taken_seats_players().items():
            player["cards"] = self.deck.draw(2)

    def do_next_turn(self):
        pass

    def get_empty_seats(self) -> list:
        empty_seats = []

        for seat, player in self.seats_players.items():
            if not player:
                empty_seats.append(seat)

        return empty_seats

    def get_taken_seats(self) -> list:
        taken_seats = []

        for seat, player in self.seats_players.items():
            if player:
                taken_seats.append(seat)

        return taken_seats

    def get_taken_seats_players(self) -> dict:
        taken_seats_players = {}

        for seat, player in self.seats_players.items():
            if player:
                taken_seats_players[seat] = player

        return taken_seats_players

    def n_empty_seats(self) -> int:
        return len(self.get_empty_seats())

    def n_taken_seats(self) -> int:
        return len(self.get_taken_seats())

    def n_total_seats(self) -> int:
        return len(self.seats_players.items())

    def on_start(self):
        self.update_dealer_and_blind_seats()
        self.place_blinds()

        self.reset_deck()
        self.deal_player_cards()

        log(f"Game started at table '{self.name}'")

        # while not game over etc:
        self.action_on_next_player()

    def place_blinds(self):
        assert self.n_taken_seats() >= 2, "need 2 or more players to place blinds"

        self.seats_players[self.small_blind_seat]["bet"] = 1
        self.seats_players[self.big_blind_seat]["bet"] = 2

        log(f"Placed blinds - SB: 1, BB: 2", LOG_INFO)

    def reset_deck(self):
        self.deck.shuffle()

    def send_player(self, target_player: dict, packet):
        for connection, player in self.server.connections_players:
            if player == target_player:
                self.server.send_single(connection, packet)

    def send_players(self, packet):
        for _, target_player in self.seats_players:
            self.send_player(target_player, packet)

    def update_dealer_and_blind_seats(self):
        if self.n_taken_seats() < 2:
            log(f"Ignoring update dealer/blinds call with < 2 players", LOG_ERROR)
            return

        # todo players new to table always pay big blind, exclude from list

        taken_seats = self.get_taken_seats()

        if not self.dealer_seat:  # dealer/blind seats not set
            new_dealer_index = random.randint(0, len(taken_seats) - 1)
            new_dealer_seat = taken_seats[new_dealer_index]

            if self.n_taken_seats() == 2:
                self.dealer_seat = new_dealer_seat
                self.small_blind_seat = new_dealer_seat
                self.big_blind_seat = taken_seats[(new_dealer_index + 1) % len(taken_seats)]

            else:
                self.dealer_seat = new_dealer_seat
                self.small_blind_seat = taken_seats[(new_dealer_index + 1) % len(taken_seats)]
                self.big_blind_seat = taken_seats[(new_dealer_index + 2) % len(taken_seats)]

            log(f"Placed D, SB, BB buttons: {self.dealer_seat}, {self.small_blind_seat}, {self.big_blind_seat}")
            return

        old_dealer_seat = self.dealer_seat
        new_dealer_seat = 0
        new_dealer_index = None  # can be 0
        for i, taken_seat in enumerate(taken_seats):
            if taken_seat > old_dealer_seat:
                new_dealer_index = i
                new_dealer_seat = taken_seat
                break

        if not new_dealer_seat:  # happens if dealer seat was the last taken seat
            new_dealer_index = 0
            new_dealer_seat = taken_seats[0]  # new seat is the first taken seat

        assert new_dealer_seat and new_dealer_index is not None, f"what, {new_dealer_seat} {new_dealer_index}"

        if self.n_taken_seats() == 2:
            self.dealer_seat = new_dealer_seat
            self.small_blind_seat = new_dealer_seat
            self.big_blind_seat = taken_seats[(new_dealer_index + 1) % len(taken_seats)]

        else:
            self.dealer_seat = new_dealer_seat
            self.small_blind_seat = taken_seats[(new_dealer_index + 1) % len(taken_seats)]
            self.big_blind_seat = taken_seats[(new_dealer_index + 2) % len(taken_seats)]

        log(f"Moved D button - {old_dealer_seat} -> {new_dealer_seat}, SB, BB: {self.small_blind_seat}, {self.big_blind_seat}")
