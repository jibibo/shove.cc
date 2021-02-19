from server_util import *
from base_game import BaseGame
from player import Player
from .deuces_custom import Card, Deck, Evaluator


STREET_PREFLOP = "PREFLOP"
STREET_FLOP = "FLOP"
STREET_TURN = "TURN"
STREET_RIVER = "RIVER"


class NoMoreStreets(Exception):
    pass


class StreetEnded(Exception):
    pass


class Poker(BaseGame):
    def __init__(self, table):
        super().__init__(table)
        self.small_blind_amount = 1

        self.action_seat = 0
        self.big_blind_amount = 2 * self.small_blind_amount
        self.big_blind_seat = 0
        self.dealer_seat = 0  # not set
        self.small_blind_seat = 0
        self.highest_bet_this_street = 0
        self.players = []
        self.community_cards: List[int] = []
        self.deck: Deck = None
        self.game_over = False
        self.pot = None  # todo temp, pot management is difficult
        # self.pots = {}
        self.street = None

    def action_on_next_player(self):
        action_player = self.get_player_in_seat(self.action_seat)
        log(f"Action on {action_player}")

        if action_player.is_bot:
            action_player.bot_action(self)

        else:
            for connection, player in self.table.server.connections_players.items():
                if action_player == player:
                    self.table.server.outgoing_packets.put((connection, {
                        "model": "action_on_you",
                        "street": self.street,
                        "players": self.players
                    }))

    def add_bets_to_pots(self):
        log("Adding bets to pots...")

        for player in self.players:
            self.pot += player["bet"]
            player["bet"] = 0

        # lowest_bet = 0
        #
        # player_bets_remaining = {player: player["bet"] for player in self.players}
        #
        # pot_number = 0
        # while player_bets_remaining:  # there are still bets left to process and add to pot
        #     players_in_pot = list(player_bets_remaining.keys())
        #     if len(players_in_pot) == 1:
        #
        #         log(f"Returned {player_bets_remaining[player]} excess chips to {player}")
        #         break
        #
        #     pot_number += 1
        #     self.pots[pot_number] = {"players": [], "size": 0}
        #
        #     log(f"Created pot number {pot_number}...")
        #
        #     for player, bet in player_bets_remaining.items():
        #         if bet < lowest_bet or not lowest_bet:
        #             lowest_bet = bet
        #
        #     log(f"Lowest bet: {lowest_bet}")
        #     self.pots[pot_number]["players"] = players_in_pot
        #     self.pots[pot_number]["size"] = lowest_bet * len(players_in_pot)
        #     log(f"Pot size: {self.pots[pot_number]['size']}")
        #
        #     for player, bet in player_bets_remaining.items():
        #         player_bets_remaining[player] -= lowest_bet
        #         if not player_bets_remaining[player]:  # all player's chips have been added to pot
        #             log(f"Collected all chips of {player}")
        #             del player_bets_remaining[player]

        log(f"Added bets to pots, total pot: {self.pot}")

    def deal_community_cards(self, test_full_game=False):
        assert self.street in [STREET_FLOP, STREET_TURN, STREET_RIVER], f"invalid street {self.street}"

        if test_full_game:
            log("Dealing community cards, full game (test)...")
            for street in [STREET_FLOP, STREET_TURN, STREET_RIVER]:
                self.street = street
                self.deal_community_cards()

            log("Done dealing community cards, full game (test)")
            return

        if self.street == STREET_FLOP:
            n_cards = 3
        else:
            n_cards = 1

        drawn_cards = self.deck.draw(n_cards)
        self.community_cards.extend(drawn_cards)
        log(f"{self.street} dealt: {Card.get_pretty_str(self.community_cards)}", LOG_INFO)

    def deal_player_cards(self):
        log("Dealing cards to players...")

        for player in self.players:
            drawn_cards = self.deck.draw(2)
            player["cards"] = drawn_cards
            log(f"Dealt cards to {player}: {Card.get_pretty_str(drawn_cards)}", LOG_INFO)

    def get_active_players(self):
        return [player for player in self.players if player["active"]]

    def get_not_folded_players(self):
        return [player for player in self.players if not player["folded"]]

    def get_player_in_seat(self, seat: int) -> Player:
        for player in self.players:
            if player["seat"] == seat:
                return player

        log(f"No player in seat: {seat}", LOG_ERROR)

    def get_seats(self):
        return [player["seat"] for player in self.players]

    def handle_event(self, event):
        pass

    def next_street(self):
        if self.street is None:
            self.street = STREET_PREFLOP

        elif self.street == STREET_PREFLOP:
            self.street = STREET_FLOP

        elif self.street == STREET_FLOP:
            self.street = STREET_TURN

        elif self.street == STREET_TURN:
            self.street = STREET_RIVER

        elif self.street == STREET_RIVER:
            raise NoMoreStreets

        if self.street in [STREET_FLOP, STREET_TURN, STREET_RIVER]:
            self.deal_community_cards()

        log(f"Next street started: {self.street}")

    def on_showdown(self):  # todo handle side pots
        log(f"Showdown started")

        players = self.get_not_folded_players()

        evaluator = Evaluator()
        winners, best_hand = evaluator.get_winners(self.community_cards, players)

        log(f"Pot winners: {winners} with {best_hand}")

        chips_won_fraction = int(self.pot / len(winners))  # todo give last aggressor the chip if uneven
        for winner in winners:
            winner.won_chips(chips_won_fraction)

    def place_blinds(self):
        # assert self.n_taken_seats() >= 2, "need 2 or more players to place blinds"  # safety check

        log(f"Placing blinds... small: 1, big: 2", LOG_INFO)
        small_blind_player = self.get_player_in_seat(self.small_blind_seat)
        big_blind_player = self.get_player_in_seat(self.big_blind_seat)

        small_blind_player.bet(1)
        big_blind_player.bet(2)

        self.highest_bet_this_street = 2

    def reset_deck(self):
        self.deck = Deck()
        self.deck.shuffle()

    def reset_pot(self):
        self.pot = 0

    def start(self):
        self.players = sorted([player for player in self.table.seats_players.values() if player],
                              key=lambda p: p["seat"], reverse=False)

        log(f"Game started! Players: {self.players}", LOG_INFO)

        for player in self.players:
            if player["chips"] > 0:
                player["active"] = True

            else:
                player["active"] = False

        self.community_cards = []
        self.reset_pot()
        self.reset_deck()
        self.update_dealer_and_blind_seats()
        self.place_blinds()
        self.deal_player_cards()

        # self.update_action_seat()
        # self.action_on_next_player()

        self.add_bets_to_pots()
        self.street = STREET_FLOP
        self.deal_community_cards(test_full_game=True)
        self.on_showdown()
        log("Game ended!", LOG_INFO)
        self.table.started = False

    def update_action_seat(self):
        pass

    def update_dealer_and_blind_seats(self):
        # if self.n_taken_seats() < 2:  # safety check
        #     log(f"Ignoring update dealer/blinds call with < 2 players", LOG_ERROR)
        #     return

        # todo players new to table always pay big blind

        log(f"Updating dealer and blind seats...")
        seats = self.get_seats()
        n_seats = len(seats)
        old_dealer_seat = self.dealer_seat

        if not old_dealer_seat:  # dealer/blind seats not set
            new_dealer_seat_index = random.randint(0, n_seats - 1)

        else:
            new_dealer_seat_index = 0  # not changed if old dealer seat was the last occupied seat
            for i, seat in enumerate(seats):
                if seat > old_dealer_seat:
                    new_dealer_seat_index = i
                    break

        new_dealer_seat = seats[new_dealer_seat_index]
        self.dealer_seat = new_dealer_seat

        if n_seats == 2:  # in heads up the dealer is the small blind
            log("Selecting blind seats for heads up...")
            self.small_blind_seat = new_dealer_seat
            self.big_blind_seat = seats[(new_dealer_seat_index + 1) % n_seats]
        else:
            log("Selecting blind seats for non-heads up...")
            self.small_blind_seat = seats[(new_dealer_seat_index + 1) % n_seats]
            self.big_blind_seat = seats[(new_dealer_seat_index + 2) % n_seats]

        log(f"Updated seats! D: {old_dealer_seat} -> {new_dealer_seat}, SB: {self.small_blind_seat}, BB: {self.big_blind_seat}")

