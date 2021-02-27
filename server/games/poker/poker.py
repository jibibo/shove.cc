from server_util import *
from base_game import BaseGame
from player import Player
from .deuces_custom import Card, Deck, Evaluator
from .pot import Pot


# todo it is supposed to be called holdem


STREET_PREFLOP = "PREFLOP"
STREET_FLOP = "FLOP"
STREET_TURN = "TURN"
STREET_RIVER = "RIVER"


class StartShowdown(Exception):
    pass


class StreetEnded(Exception):
    pass


class Poker(BaseGame):
    def __init__(self, table):
        super().__init__(table)

        self.action_seat: int = 0
        self.big_blind_seat = 0
        self.community_cards: List[int] = []
        self.dealer_seat = 0
        self.deck: Deck = Deck()
        self.last_aggressor = None
        self.last_bet = 0
        self.n_hands_played = 0
        self.players = []
        self.pots: List[Pot] = []
        self.small_blind_amount = 1
        self.small_blind_seat = 0
        self.street = None
        self.big_blind_amount = 2 * self.small_blind_amount

        self.total_elapsed = 0  # testing purposes

    def action_on_seat(self):
        action_player = self.get_player_in_seat(self.action_seat)
        Log.info(f"Action on {action_player}")

        if action_player.is_bot:
            action_player.decide_bot_action(self)

            if action_player["bet"] > self.last_bet:
                self.last_bet = action_player["bet"]

                for player in self.players:
                    if player == action_player:
                        continue

                    player["manual_bet_matches"] = False

        else:  # todo abstract player object should have connection socket (and Account object?)
            for connection, player in self.table.server.connections_players.items():
                if action_player == player:
                    self.table.server.outgoing_packets.put((connection, {
                        "model": "action",
                        "street": self.street,
                        "players": self.players
                    }))

    def add_bets_to_pots(self):
        Log.trace("Adding bets to pots")

        player_bets_remaining = {player: player["bet"] for player in self.players}

        while player_bets_remaining:
            player_bets_remaining_formatted = {player['username']: bet for player, bet in player_bets_remaining.items()}
            Log.trace(f"Player bets remaining: {player_bets_remaining_formatted}")
            players = list(player_bets_remaining.keys())

            if len(players) == 1:
                player = players[0]
                player.return_bet_to_player(player_bets_remaining[player])
                break

            pot = None
            for existing_pot in self.pots:
                if existing_pot.players == players:
                    pot = existing_pot
                    Log.trace(f"Using existing pot {pot}")
                    break

            if not pot:
                Log.trace(f"No suitable existing pot found, creating new one")
                pot = Pot(players, pot_number=len(self.pots))
                self.pots.append(pot)

            lowest_bet: int = min([bet for bet in player_bets_remaining.values()])
            if not lowest_bet:
                Log.trace(f"Nobody has bet this round, continuing")
                break

            Log.trace(f"Lowest bet: {lowest_bet}")

            for player in list(player_bets_remaining.keys()):
                if player_bets_remaining[player] == lowest_bet:
                    Log.trace(f"Added bet chips of {player} to pot")
                    del player_bets_remaining[player]
                    continue

                player_bets_remaining[player] -= lowest_bet
                Log.trace(f"Reduced bet of {player} to {player_bets_remaining[player]}")

            pot.chips += lowest_bet * len(players)
            Log.trace(f"{pot} now has {pot.chips} chips")

    def deal_community_cards(self, deal_all_streets=False):
        if deal_all_streets:  # testing only, can easily break the game
            Log.trace("Dealing all streets")
            for street in [STREET_FLOP, STREET_TURN, STREET_RIVER]:
                self.street = street
                self.deal_community_cards()

            Log.trace("Done dealing all streets")
            return

        if self.street == STREET_FLOP:
            n_cards = 3
        else:
            n_cards = 1

        drawn_cards = self.deck.draw(n_cards)
        self.community_cards.extend(drawn_cards)
        # todo send a packet here with only the newly drawn cards, not including all the old ones

        Log.info(f"Community cards: {Card.get_pretty_str(self.community_cards)}")

    def deal_player_cards(self):
        Log.trace("Dealing cards to all players")

        for player in self.players:
            drawn_cards = self.deck.draw(2)
            player["cards"] = drawn_cards
            Log.debug(f"Dealt cards to {player}: {Card.get_pretty_str(drawn_cards)}")

        Log.trace("Dealt cards to all players")

    def get_next_action_seat(self, start_seat, last_action_seat) -> int:
        """Returns next action seat that can have action, 0 if betting round over"""

        Log.trace("Getting next action seat")
        seats = self.get_seats()
        assert start_seat in seats and (last_action_seat is None or last_action_seat in seats), "no valid start/last_action seat"

        # reorder player list to check in order, starting at player in seat start_seat, excl. last action player
        players_cycled = self.players.copy()
        while players_cycled[0]["seat"] != start_seat:  # should never be an infinite loop
            players_cycled.append(players_cycled.pop(0))

        Log.trace(f"Possible action seats: {[player['seat'] for player in players_cycled]}")

        for player in players_cycled:
            player_seat = player["seat"]
            Log.trace(f"Evaluating player in seat {player_seat}")

            if player_seat == last_action_seat:
                Log.trace(f"Skipped {player} for action: last action seat")
                continue

            if player["manual_bet_matches"]:
                Log.trace(f"Skipped {player} for action: manual bet matches")
                continue

            if player["all_in"]:
                Log.trace(f"Skipped {player} for action: is all-in")
                continue

            if player["folded"]:
                Log.trace(f"Skipped {player} for action: has folded")
                continue

            Log.debug(f"Got valid next action seat: {player_seat}")
            return player_seat

        Log.debug("Betting round over")
        return 0

    def get_not_folded_players(self):
        return [player for player in self.players if not player["folded"]]

    def get_player_in_seat(self, seat: int) -> Player:
        for player in self.players:
            if player["seat"] == seat:
                return player

        Log.error(f"No player in seat: {seat}")

    def get_seats(self):
        return [player["seat"] for player in self.players]

    def handle_event(self, event):
        pass

    def post_blinds(self):
        # assert self.n_taken_seats() >= 2, "need 2 or more players to place blinds"  # safety check

        Log.debug(f"Posting blinds")
        small_blind_player = self.get_player_in_seat(self.small_blind_seat)
        big_blind_player = self.get_player_in_seat(self.big_blind_seat)

        small_blind_player.post_blind(self.small_blind_amount)
        big_blind_player.post_blind(self.big_blind_amount)

        self.last_bet = 2
        self.last_aggressor = big_blind_player

    @staticmethod
    def process_pocket_cards_winners(best_hands):
        """
        HEADS-UP WITHOUT FOLDING/BETTING ONLY
        Add data to dataset of what pocket cards have the highest win percentage
        """

        players = []
        winners = []
        best_rank = 7463
        for player, rank, _, _ in best_hands:
            players.append(player)

            if rank < best_rank:
                winners = [player]
                best_rank = rank
            elif rank == best_rank:
                winners.append(player)

        for player in players:
            cards = player["cards"]
            rank_ints = []
            suit_ints = []
            for card in cards:
                rank_ints.append(Card.get_rank_int(card))
                suit_ints.append(Card.get_suit_int(card))

            if rank_ints[0] < rank_ints[1]:
                rank_ints.append(rank_ints.pop(0))

            suited = suit_ints[0] == suit_ints[1]
            pair = rank_ints[0] == rank_ints[1]

            if pair:
                suffix = ""
            else:
                if suited:
                    suffix = "s"
                else:
                    suffix = "o"

            cards_formatted = f"{Card.STR_RANKS[rank_ints[0]]}{Card.STR_RANKS[rank_ints[1]]}{suffix}"

            with open("pocket_cards.json", "r") as f:
                pocket_cards = json.load(f)

            pocket_cards[cards_formatted]["dealt"] += 1
            Log.test(f"incremented times dealt of {cards_formatted}")

            if player in winners:
                pocket_cards[cards_formatted]["won"] += 1
                Log.test(f"incremented times won of {cards_formatted}")

            with open("pocket_cards.json", "w") as f:
                json.dump(pocket_cards, f, indent=4)

    def set_next_street_and_deal(self):
        if self.street is None:
            self.street = STREET_PREFLOP

        elif self.street == STREET_PREFLOP:
            self.street = STREET_FLOP

        elif self.street == STREET_FLOP:
            self.street = STREET_TURN

        elif self.street == STREET_TURN:
            self.street = STREET_RIVER

        elif self.street == STREET_RIVER:
            raise StartShowdown

        else:
            raise AssertionError("current street is invalid")

        Log.info(f"Street started: {self.street}")

        if self.street in [STREET_FLOP, STREET_TURN, STREET_RIVER]:
            self.deal_community_cards()

    def start(self):  # todo is only called once (as soon as enough players at table)
        self.players = sorted([player for player in self.table.seats_players.values()
                               if player is not None and
                               player["chips"] > 0],
                              key=lambda p: p["seat"], reverse=False)

        if len(self.players) < 2:
            Log.warn("Not enough players with chips to start")
            return

        self.running = True
        self.start_hand()

    def start_hand(self):  # todo starts new hand, moves dealer button, etc.
        # hand progression explained:
        # https://www.instructables.com/Learn-To-Play-Poker---Texas-Hold-Em-aka-Texas-Ho/

        self.n_hands_played += 1
        start_time = time.time()
        Log.info(f"Hand #{self.n_hands_played} started! Players: {self.players}")

        for player in self.players:
            player.new_hand_starting()

        self.street = None
        self.pots = [Pot(self.players)]
        self.community_cards = []
        self.deck = Deck()
        self.deck.shuffle()
        self.update_dealer_blind_action_seats()
        self.post_blinds()
        self.deal_player_cards()

        while True:
            try:
                self.set_next_street_and_deal()  # sets to PREFLOP if necessary
            except StartShowdown:
                Log.trace("Caught StartShowdown, starting showdown")
                self.start_showdown()
                break

            seats = self.get_seats()
            if self.street != STREET_PREFLOP:
                # once the next street starts, all players can bet again
                self.last_bet = 0
                self.last_aggressor = None
                Log.trace("Setting player's bet matches to False")
                for player in self.players:
                    player["manual_bet_matches"] = False
                    player["bet"] = 0

                start_seat = seats[(seats.index(self.dealer_seat) + 1) % len(seats)]
                self.action_seat = self.get_next_action_seat(start_seat, None)

            while self.action_seat:
                self.action_on_seat()

                # start looking for next action-eligible player at seat after the seat who just had action
                start_seat = seats[(seats.index(self.action_seat) + 1) % len(seats)]
                self.action_seat = self.get_next_action_seat(start_seat, self.action_seat)

            self.add_bets_to_pots()

        elapsed_time = time.time() - start_time
        Log.test(f"Hand finished in {round(elapsed_time * 1000)}ms")
        self.total_elapsed += elapsed_time
        Log.test(f"Hands played: {self.n_hands_played}, average time: {round(self.total_elapsed / self.n_hands_played * 1000)}ms")

        self.running = False

    def start_showdown(self):  # todo handle side pots
        Log.info(f"Showdown started!")

        players = self.get_not_folded_players()

        best_hands = Evaluator.get_best_hands(self.community_cards, players)  # [(player, %, hand)]

        for pot in self.pots:
            pot.distribute_chips(best_hands)

        Poker.process_pocket_cards_winners(best_hands)

    def update_dealer_blind_action_seats(self):
        # if self.n_taken_seats() < 2:  # safety check
        #     log(f"Ignoring update dealer/blinds call with < 2 players", LEVEL_ERROR)
        #     return

        # todo players new to table always pay big blind

        Log.debug(f"Updating dealer and blind seats")
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
            Log.trace("Selecting blind/action seats for heads up")
            self.small_blind_seat = new_dealer_seat
            self.big_blind_seat = seats[(new_dealer_seat_index + 1) % n_seats]
            self.action_seat = new_dealer_seat  # todo take into account if player is not active
        else:
            Log.trace("Selecting blind/action seats for non-heads up")
            self.small_blind_seat = seats[(new_dealer_seat_index + 1) % n_seats]
            self.big_blind_seat = seats[(new_dealer_seat_index + 2) % n_seats]
            self.action_seat = seats[(new_dealer_seat_index + 3) % n_seats]  # todo take into account if player is not active

        if old_dealer_seat > 0:
            old_dealer_seat_formatted = old_dealer_seat
        else:
            old_dealer_seat_formatted = "(not set)"

        Log.info(f"Updated seats, D: {old_dealer_seat_formatted} -> {new_dealer_seat}, SB: {self.small_blind_seat}, BB: {self.big_blind_seat}")
