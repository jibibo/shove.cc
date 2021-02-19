import itertools
from server_util import *
from .card import Card
from .lookup_table import LookupTable


class Evaluator:
    """
    Evaluates hand strengths using a variant of Cactus Kev's algorithm:
    http://suffe.cool/poker/evaluator.html
    I make considerable optimizations in terms of speed and memory usage,
    in fact the lookup table generation can be done in under a second and
    consequent evaluations are very fast. Won't beat C, but very fast as
    all calculations are done with bit arithmetic and table lookups.
    """

    def __init__(self):
        self.lookup_table = LookupTable()

        self.hand_size_map = {
            5: self._five,
            6: self._six,
            7: self._seven
        }

    def _five(self, card_int_list):
        """
        Performs an evaluation given cards in integer form, mapping them to
        a rank in the range [1, 7462], with lower ranks being more powerful.
        Variant of Cactus Kev's 5 card evaluator, though I saved a lot of memory
        space using a hash table and condensing some of the calculations.
        """

        # if flush todo cleanup
        if card_int_list[0] & card_int_list[1] & card_int_list[2] & card_int_list[3] & card_int_list[4] & 0xF000:
            hand_or = (card_int_list[0] | card_int_list[1] | card_int_list[2] | card_int_list[3] | card_int_list[4]) >> 16
            prime = Card.prime_product_from_rankbits(hand_or)
            return self.lookup_table.flush_lookup[prime]

        else:
            prime = Card.prime_product_from_hand(card_int_list)
            return self.lookup_table.unsuited_lookup[prime]

    def _six(self, cards):
        """
        Performs five_card_eval() on all (6 choose 5) = 6 subsets
        of 5 cards in the set of 6 to determine the best ranking,
        and returns this ranking.
        """

        minimum = LookupTable.MAX_HIGH_CARD

        all_5_card_combos = itertools.combinations(cards, 5)
        for combo in all_5_card_combos:

            score = self._five(combo)
            if score < minimum:
                minimum = score

        return minimum

    def _seven(self, cards):
        """
        Performs five_card_eval() on all (7 choose 5) = 21 subsets
        of 5 cards in the set of 7 to determine the best ranking,
        and returns this ranking.
        """

        minimum = LookupTable.MAX_HIGH_CARD

        all_5_card_combos = itertools.combinations(cards, 5)
        for combo in all_5_card_combos:
            score = self._five(combo)
            if score < minimum:
                minimum = score

        return minimum

    def evaluate(self, cards, board):
        """
        This is the function that the user calls to get a hand rank.
        Supports empty board, etc very flexible. No input validation
        because that's cycles!
        """

        all_cards = cards + board
        return self.hand_size_map[len(all_cards)](all_cards)

    @staticmethod
    def get_rank_class(hand_rank):
        """
        Returns the class of hand given the hand_rank
        returned from evaluate.
        """

        if 0 <= hand_rank <= LookupTable.MAX_STRAIGHT_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT_FLUSH]
        if hand_rank <= LookupTable.MAX_FOUR_OF_A_KIND:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FOUR_OF_A_KIND]
        if hand_rank <= LookupTable.MAX_FULL_HOUSE:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FULL_HOUSE]
        if hand_rank <= LookupTable.MAX_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FLUSH]
        if hand_rank <= LookupTable.MAX_STRAIGHT:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT]
        if hand_rank <= LookupTable.MAX_THREE_OF_A_KIND:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_THREE_OF_A_KIND]
        if hand_rank <= LookupTable.MAX_TWO_PAIR:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_TWO_PAIR]
        if hand_rank <= LookupTable.MAX_PAIR:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_PAIR]
        if hand_rank <= LookupTable.MAX_HIGH_CARD:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_HIGH_CARD]

        raise Exception("Hand rank exceeds worst possible high-card hand")  # todo handle this ex

    @staticmethod
    def class_to_string(class_int):
        """
        Converts the integer class hand score into a human-readable string.
        """

        return LookupTable.RANK_CLASS_TO_STRING[class_int]

    @staticmethod
    def get_five_card_rank_percentile(hand_rank):
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """

        return float(hand_rank) / float(LookupTable.MAX_HIGH_CARD)

    def get_winners(self, board, players) -> tuple:  # todo cleanup
        """
        Returns (winners, best hand) based on each player's hand rank
        """

        assert len(board) == 5, f"Invalid board length ({len(board)})"

        for player in players:
            assert len(player["cards"]) == 2, f"Invalid hand length ({len(player['cards'])})"

        best_rank = 7463  # rank one worse than worst hand todo why one worse
        best_hand = ""
        winners = []

        for player in players:
            rank = self.evaluate(player["cards"], board)
            rank_class = self.get_rank_class(rank)
            class_string = self.class_to_string(rank_class)
            percentile = self.get_five_card_rank_percentile(rank)
            log(f"{player} has {class_string}, top {round(percentile * 100, 1)}%")

            # detect if player is a winner
            if rank == best_rank:
                winners.append(player)
                best_rank = rank
                best_hand = class_string

            elif rank < best_rank:
                winners = [player]
                best_rank = rank
                best_hand = class_string

        return winners, best_hand