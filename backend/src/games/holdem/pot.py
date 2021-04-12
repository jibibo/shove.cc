from src.convenience import *


class Pot:
    def __init__(self, participants, side_pot_number=0):
        self.participants: list = participants
        self.chips = 0
        self.side_pot_number = side_pot_number

        if side_pot_number:
            self.pot_name = f"Side Pot #{side_pot_number}"
        else:
            self.pot_name = f"Main Pot"

        Log.trace(f"{self.pot_name} created, participants: {participants}")

    def __str__(self):
        return f"'{self.pot_name}'"

    def distribute_chips_to_best_hands(self, best_hands):
        pot_winners = []
        best_name = None
        best_rank = 7463
        best_percentile = 1

        for player, name, rank, percentile in best_hands:
            if player not in self.participants:  # player is not eligible for this pot
                continue

            if rank < best_rank:
                pot_winners = [player]
                best_name = name
                best_rank = rank
                best_percentile = percentile
            elif rank == best_rank:
                pot_winners.append(player)

        self.give_chips_to_pot_winners(pot_winners, best_name, best_rank, best_percentile)

    def give_chips_to_pot_winners(self, winners, name, rank, percentile):
        chips_per_winner = int(self.chips / len(winners))  # todo odd chip goes to last aggressor
        for winner in winners:
            winner.won_chips(chips_per_winner, name, rank, percentile)

        Log.trace(f"Given {self.pot_name} winnings to {[winner['username'] for winner in winners]} ({chips_per_winner} chips/winner)")

    def remove_folded_player(self, player):
        if player in self.participants:
            self.participants.remove(player)
            Log.trace(f"Removed {player} from participants of {self}")
