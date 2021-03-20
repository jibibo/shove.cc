from convenience import *
from base_game import BaseGame

from .player import Player
from .deuces_custom import Card, Deck, Evaluator
from .pot import Pot


STREET_PREFLOP = "PREFLOP"
STREET_FLOP = "FLOP"
STREET_TURN = "TURN"
STREET_RIVER = "RIVER"


class StartShowdown(Exception):
    pass


class StreetEnded(Exception):
    pass


class Holdem(BaseGame):
    def __init__(self, room):
        super().__init__(room)

        self.big_blind_seat = 0
        self.blind_amount = 1
        self.community_cards: List[int] = []
        self.dealer_seat = 0
        self.deck: Deck = Deck()
        self.last_aggressor = None
        self.last_bet = 0
        self.n_hands_played = 0
        self.players = []
        self.pots: List[Pot] = []
        self.small_blind_seat = 0
        self.street = None
        # self.n_seats = 10
        # self.seats_players = dict.fromkeys(range(1, self.n_seats + 1))

        self.total_elapsed = 0  # testing purposes

    def action_on_player(self, action_player: Player):
        Log.info(f"Action on seat {action_player['seat']}: {action_player}, to call: {self.last_bet - action_player['bet']}")

        if action_player.is_bot:
            action_player.decide_bot_action(self)

            if action_player["folded"]:
                for pot in self.pots:
                    pot.remove_folded_player(action_player)

            elif action_player["bet"] > self.last_bet:
                self.last_bet = action_player["bet"]

                for player in self.players:
                    if player == action_player:
                        continue

                    player["had_action"] = False

                Log.trace(f"Set other player's had_action to False")

        else:  # todo abstract player object should have connection socket (and Account object?)
            for connection, player in self.room.shove.connections_players.items():
                if action_player == player:
                    self.room.shove.outgoing_packets.put((connection, {
                        "model": "action",
                        "street": self.street,
                        "players": self.players
                    }))

    def add_bets_to_pots(self):
        Log.trace("Adding bets to pots")

        player_bets_remaining = {player: player["bet"] for player in self.players if player["bet"]}

        while player_bets_remaining:
            player_bets_remaining_formatted = {player['username']: bet for player, bet in player_bets_remaining.items()}
            Log.trace(f"Player bets remaining: {player_bets_remaining_formatted}")
            players_remaining = [player for player in player_bets_remaining.keys()]
            players_remaining_not_folded = [player for player in players_remaining if not player["folded"]]

            if len(players_remaining) == 1:
                player, excess_chips = list(player_bets_remaining.items())[0]
                player.return_excess_chips(excess_chips)
                break

            lowest_bet: int = min([bet for bet in player_bets_remaining.values()])
            if not lowest_bet:
                Log.trace(f"Nobody has bet this round, continuing")
                break

            Log.trace(f"Lowest remaining bet: {lowest_bet}")

            if self.pots:  # main pot already exists (and perhaps side pots)
                pot = None

                for existing_pot in self.pots:
                    if existing_pot.participants == players_remaining_not_folded:
                        pot = existing_pot
                        Log.trace(f"Using existing pot {pot}")
                        break

                if not pot:
                    Log.trace(f"No suitable (side)pot found, creating new side pot")
                    pot = Pot(players_remaining_not_folded, side_pot_number=len(self.pots))
                    self.pots.append(pot)

            else:
                Log.trace("Main pot not does not exist, creating it")
                pot = Pot(players_remaining_not_folded)
                self.pots = [pot]

            for player, bet in list(player_bets_remaining.items()):
                player_bets_remaining[player] -= lowest_bet

                if player_bets_remaining[player] == 0:
                    Log.trace(f"{player} has no bet chips left")
                    del player_bets_remaining[player]
                    continue

                Log.trace(f"Reduced bet of {player} to {player_bets_remaining[player]}")

            pot.chips += lowest_bet * len(players_remaining)
            Log.trace(f"{pot} now has {pot.chips} chips")

    def get_next_action_player(self, start_seat, last_player) -> Player:
        """Returns next player that can have action, 0 if betting round over"""

        Log.debug("Getting next action player")
        seats = self.get_seats()
        assert start_seat in seats, f"invalid start seat: {start_seat}"

        # reorder player list to check in order, starting at player in seat start_seat, excl. last action player
        players_cycled = [player for player in self.players if player != last_player]

        while players_cycled[0]["seat"] != start_seat:  # should never be an infinite loop, who knows
            players_cycled.append(players_cycled.pop(0))

        Log.trace(f"Possible action seats: {[player['seat'] for player in players_cycled]}")

        for player in players_cycled:
            player_seat = player["seat"]
            Log.trace(f"Evaluating player in seat {player_seat}")

            if player["all_in"]:
                Log.trace(f"Skipped {player} for action: is all-in")
                continue

            if player["folded"]:
                Log.trace(f"Skipped {player} for action: has folded")
                continue

            if player["had_action"]:
                Log.trace(f"Skipped {player} for action: already had action")
                continue

            Log.debug(f"Got valid next action player: {player}")
            return player

        Log.debug("Betting round over")

    def get_not_folded_players(self):
        return [player for player in self.players if not player["folded"]]

    def get_player_in_seat(self, seat: int) -> Player:
        for player in self.players:
            if player["seat"] == seat:
                return player

        Log.warn(f"No player in seat: {seat}")

    def get_seats(self):  # always ordered, as self.players is ordered upon hand start
        return [player["seat"] for player in self.players]

    # todo implement
    # def get_empty_seats(self) -> list:
    #     empty_seats = []
    #
    #     for seat, player in self.seats_players.items():
    #         if player is None:
    #             empty_seats.append(seat)
    #
    #     return empty_seats
    #
    # def get_taken_seats(self) -> list:
    #     taken_seats = []
    #
    #     for seat, player in self.seats_players.items():
    #         if player:
    #             taken_seats.append(seat)
    #
    #     return taken_seats
    #
    # def get_taken_seats_players(self) -> dict:
    #     taken_seats_players = {}
    #
    #     for seat, player in self.seats_players.items():
    #         if player:
    #             taken_seats_players[seat] = player
    #
    #     return taken_seats_players
    #
    # def n_empty_seats(self) -> int:
    #     return len(self.get_empty_seats())
    #
    # def n_taken_seats(self) -> int:
    #     return len(self.get_taken_seats())
    #
    # def n_total_seats(self) -> int:
    #     total_seats = len(self.seats_players.items())
    #     return total_seats
    #
    # def put_player_in_seat(self, player: Player, seat: int):
    #     player["seat"] = seat
    #     self.seats_players[seat] = player  # todo should just be a list of player obj with seat property
    #     Log.info(f"Put player {player} in seat {seat}")

    def handle_event(self, event):
        pass

    def post_blinds(self, small_blind_player, big_blind_player):
        # assert self.n_taken_seats() >= 2, "need 2 or more players to place blinds"  # safety check

        Log.debug(f"Posting blinds")
        small_blind_player.post_blind(self.blind_amount)
        big_blind_player.post_blind(2 * self.blind_amount)

        # todo this might go wrong if the blind player is forced to go all in
        self.last_bet = 2 * self.blind_amount
        self.last_aggressor = big_blind_player

    @staticmethod
    def process_pocket_cards_winners(best_hands):
        """
        PREVENT RAISING AND FOLDING
        Add data to dataset of what pocket cards have the highest win percentage
        """

        assert len(best_hands) == 2, "must be a heads-up game"  # to keep dataset data consistent

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
                rank_ints.append(rank_ints.pop(0))  # highest ranked card goes first (5A becomes A5)

            if rank_ints[0] == rank_ints[1]:  # pocket pair
                suffix = ""
            elif suit_ints[0] == suit_ints[1]:
                suffix = "s"  # suited
            else:
                suffix = "o"  # offsuit

            cards_formatted = f"{Card.RANKS_INT_TO_RANK_CHAR[rank_ints[0]]}{Card.RANKS_INT_TO_RANK_CHAR[rank_ints[1]]}{suffix}"

            with open("test/pocket_cards.json", "r") as f:
                pocket_cards = json.load(f)

            pocket_cards[cards_formatted]["dealt"] += 1
            Log.test(f"incremented times dealt of {cards_formatted}")

            if player in winners:
                pocket_cards[cards_formatted]["won"] += 1
                Log.test(f"incremented times won of {cards_formatted}")

            with open("test/pocket_cards.json", "w") as f:
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
            if self.street == STREET_FLOP:
                n_cards = 3
            else:
                n_cards = 1

            self.community_cards.extend(self.deck.draw(n_cards))
            Log.info(f"Community cards: {Card.get_pretty_str(self.community_cards)}")

    def start(self):  # todo is only called once (as soon as enough players at table)
        # if self.game.running:
        #     Log.info("Game already started")
        #     return

        # if self.n_taken_seats() < Room.MIN_PLAYERS:
        #     Log.info(f"Not enough players to start: {self.n_taken_seats()}/{self.MIN_PLAYERS}")
        #     return

        self.players = sorted([player for player in self.room.seats_players.values()
                               if player is not None and
                               player["chips"] > 0],
                              key=lambda p: p["seat"],
                              reverse=False)

        if len(self.players) < 2:
            Log.warn("Not enough players with chips to start")
            return

        self.running = True
        self.start_hand()

    def start_hand(self):
        # hand progression explained:
        # https://www.instructables.com/Learn-To-Play-Poker---Texas-Hold-Em-aka-Texas-Ho/

        self.n_hands_played += 1
        start_time = time.time()
        Log.info(f"Hand #{self.n_hands_played} started! Players ({len(self.players)}): {self.players}")

        for player in self.players:
            player.new_hand_started()

        self.street = None
        self.pots = []
        self.community_cards = []
        self.deck = Deck()
        self.deck.shuffle()
        self.update_buttons()
        self.post_blinds(self.get_player_in_seat(self.small_blind_seat), self.get_player_in_seat(self.big_blind_seat))
        self.deck.deal_players(self.players)

        while True:
            try:
                self.set_next_street_and_deal()  # todo if all players but one folded/all in just skip to showdown
            except StartShowdown:
                Log.trace("Caught StartShowdown, starting showdown")
                self.start_showdown()
                break

            seats = self.get_seats()
            if self.street == STREET_PREFLOP:
                if len(seats) == 2:
                    start_seat = self.dealer_seat  # in heads up, dealer has action first
                else:
                    start_seat = seats[(seats.index(self.dealer_seat) + 3) % len(seats)]  # get the seat of the "under the gun" player

            else:
                start_seat = seats[(seats.index(self.dealer_seat) + 1) % len(seats)]  # after the preflop, action starts at position AFTER the dealer

                # once the next street starts, all players can bet again
                self.last_bet = 0
                self.last_aggressor = None
                for player in self.players:
                    player.next_street_started()

            while True:
                action_player = self.get_next_action_player(start_seat, None)
                if not action_player:
                    break

                self.action_on_player(action_player)

                # start looking for next action-eligible player at seat after the seat who just had action
                start_seat = seats[(seats.index(start_seat) + 1) % len(seats)]

            self.add_bets_to_pots()

        elapsed_time = time.time() - start_time
        Log.test(f"Hand finished in {round(elapsed_time * 1000)}ms")
        self.total_elapsed += elapsed_time
        Log.test(f"Hands played: {self.n_hands_played}, average time: {round(self.total_elapsed / self.n_hands_played * 1000)}ms")

        player_chips = {player["username"]: player["chips"] for player in self.players}
        Log.trace(f"Chip count per player: {player_chips}")

        self.running = False

    def start_showdown(self):
        Log.info(f"Showdown started!")

        best_hands = Evaluator.get_best_hands(self.community_cards, self.get_not_folded_players())

        for pot in self.pots:
            pot.distribute_chips_to_best_hands(best_hands)

        # Holdem.process_pocket_cards_winners(best_hands)

    def update_buttons(self):
        if len(self.get_seats()) < 2:  # safety check
            Log.warn(f"Ignoring update buttons call with < 2 players")
            return

        Log.debug(f"Updating dealer and blind buttons")
        seats = self.get_seats()
        Log.trace(f"Seats: {seats}")
        n_seats = len(seats)
        previous_dealer_seat = self.dealer_seat

        if not previous_dealer_seat:  # dealer/blind seats not set
            new_dealer_seat_index = random.randint(0, n_seats - 1)
        else:
            new_dealer_seat_index = 0  # not changed if old dealer seat was the last occupied seat
            for i, seat in enumerate(seats):
                if seat > previous_dealer_seat:
                    new_dealer_seat_index = i
                    break

        Log.trace(f"New dealer seat index: {new_dealer_seat_index}")
        self.dealer_seat = seats[new_dealer_seat_index]

        if n_seats == 2:  # in heads up the dealer is the small blind
            Log.trace("Setting button seats for heads-up")
            self.small_blind_seat = self.dealer_seat
            self.big_blind_seat = seats[(new_dealer_seat_index + 1) % n_seats]

        else:
            Log.trace("Setting button seats for non heads-up")
            self.small_blind_seat = seats[(new_dealer_seat_index + 1) % n_seats]
            self.big_blind_seat = seats[(new_dealer_seat_index + 2) % n_seats]

        Log.debug(f"Updated button seats, D: {previous_dealer_seat if previous_dealer_seat else '(not set)'} -> {self.dealer_seat}, SB: {self.small_blind_seat}, BB: {self.big_blind_seat}")

    # todo move commented methods to (abstract) game
    # def add_bot(self, seat=None) -> int:
    #     bot_player = Player(bot_number=self.shove.get_next_bot_number())
    #     seat = self.add_player(bot_player, seat)
    #     return seat
    #
    # def add_bots(self, amount=1):
    #     added_bots = 0
    #
    #     seats = []
    #     for _ in range(amount):
    #         seat = self.add_bot()
    #         if seat:
    #             seats.append(seat)
    #             added_bots += 1
    #
    #     Log.info(f"Added {added_bots}/{amount} bots to seats {seats}")

    # def add_player(self, client_or_bot, seat=None) -> int:
    #     """Sets and returns player's seat, 0 or AssertionError if fail"""
    #
    #     if self.game.running:
    #         Log.warn("Can't add player: game running")  # todo add to a queue to join next round
    #         return 0
    #
    #     assert client_or_bot, "no player given"

    # if isinstance(client_or_bot, ConnectedClient):
    #     assert client_or_bot.player, "User is not logged in"
    #     player = client_or_bot.player
    #
    # else:
    #     assert client_or_bot.is_bot, "Neither connected user nor bot player provided"
    #     player = client_or_bot

    # empty_seats = self.get_empty_seats()
    #
    # if not empty_seats:
    #     Log.warn("No seats empty, ignoring call")
    #     return 0
    #
    # if seat:
    #     if seat in empty_seats:
    #         Log.trace(f"Given seat {seat} is available")
    #     else:
    #         Log.warn(f"Given seat {seat} is taken, choosing random seat")
    #         seat = random.choice(empty_seats)
    #
    # else:
    #     seat = random.choice(empty_seats)
    #     Log.trace(f"No seat given, chose random seat {seat}")
    #
    # self.put_player_in_seat(client_or_bot, seat)
    # self.events.put("player_added")
    # return seat
