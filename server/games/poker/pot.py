from server_util import *


class Pot:
    def __init__(self, players, pot_number=0):
        self.players = players
        self.chips = 0
        self.pot_number = pot_number

        if pot_number:
            self.pot_name = f"Side pot #{pot_number}"
            Log.trace(f"{self.pot_name} created, players: {players}")
        else:
            self.pot_name = f"Main pot"
            Log.trace(f"{self.pot_name} created")

    def __str__(self):
        return f"'{self.pot_name}'"

    def distribute_chips(self, best_hands):
        pot_winners = []
        best_rank = 7463
        best_percentile = 1
        best_hand = None

        for player, rank, percentile, hand in best_hands:
            if player not in self.players:
                continue

            if rank < best_rank:
                pot_winners = [player]
                best_rank = rank
                best_percentile = percentile
                best_hand = hand
            elif rank == best_rank:
                pot_winners.append(player)

        chips_per_winner = int(self.chips / len(pot_winners))  # todo odd chip goes to last aggressor
        for winner in pot_winners:
            winner.won_chips(chips_per_winner, best_hand, best_percentile)

        Log.trace(f"Given {self.pot_name} winnings ({chips_per_winner} chips/winner) to {[winner['username'] for winner in pot_winners]}")
