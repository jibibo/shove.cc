import itertools

from src.convenience import *
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

    @staticmethod
    def five(card_int_list):
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
            return LOOKUP_TABLE.flush_lookup[prime]

        else:
            prime = Card.prime_product_from_hand(card_int_list)
            return LOOKUP_TABLE.unsuited_lookup[prime]

    @staticmethod
    def six(card_int_list):
        """
        Performs five_card_eval() on all (6 choose 5) = 6 subsets
        of 5 cards in the set of 6 to determine the best ranking,
        and returns this ranking.
        """

        minimum = LookupTable.MAX_HIGH_CARD

        all_5_card_combos = itertools.combinations(card_int_list, 5)
        for combo in all_5_card_combos:
            score = Evaluator.five(combo)
            if score < minimum:
                minimum = score

        return minimum

    @staticmethod
    def seven(card_int_list):
        """
        Performs five_card_eval() on all (7 choose 5) = 21 subsets
        of 5 cards in the set of 7 to determine the best ranking,
        and returns this ranking.
        """

        minimum = LookupTable.MAX_HIGH_CARD

        all_5_card_combos = itertools.combinations(card_int_list, 5)
        for combo in all_5_card_combos:
            score = Evaluator.five(combo)
            if score < minimum:
                minimum = score

        return minimum

    @staticmethod
    def evaluate(cards, board):
        """
        This is the function that the user calls to get a hand rank.
        Supports empty board, etc very flexible. No input validation
        because that's cycles!
        """

        all_cards = cards + board
        return CARD_COUNT_MAP[len(all_cards)](all_cards)

    @staticmethod
    def get_best_hands(board, players) -> List[tuple]:  # todo cleanup
        """
        Returns [(player, name, rank, percentile)] based on each given player's hand's rank
        """

        Log.trace(f"Evaluating best hands, board: {Card.get_pretty_str(board)}")

        assert len(board) == 5, f"Invalid board length ({len(board)})"

        for player in players:
            assert len(player["cards"]) == 2, f"Invalid hand length ({len(player['cards'])})"

        best_hands = []
        for player in players:
            player_cards = player["cards"]
            rank = Evaluator.evaluate(player_cards, board)
            name = LookupTable.rank_to_name(rank)
            percentile = LookupTable.rank_to_percentile(rank)
            # todo only make the aggressors cards public, all others get mucked
            Log.trace(f"{player} ({Card.get_pretty_str(player_cards)}) has a {name}, rank {rank}")
            best_hands.append((player, name, rank, percentile))

        Log.trace(f"Done evaluating best hands: {best_hands}")
        return best_hands


LOOKUP_TABLE = LookupTable()
CARD_COUNT_MAP: Dict[int, callable] = {
    5: Evaluator.five,
    6: Evaluator.six,
    7: Evaluator.seven
}
