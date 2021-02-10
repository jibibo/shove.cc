import itertools
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
    def get_five_card_rank_percentage(hand_rank):
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """

        return float(hand_rank) / float(LookupTable.MAX_HIGH_CARD)

    def hand_summary(self, board, hands):
        """
        Gives a summary of the hand with ranks as time proceeds.
        Requires that the board is in chronological order for the
        analysis to make sense.
        """

        assert len(board) == 5, "Invalid board length"
        for hand in hands:
            assert len(hand) == 2, "Invalid hand length"

        line_length = 10
        stages = ["FLOP", "TURN", "RIVER"]

        for i in range(len(stages)):
            print(f"{'='* line_length} {stages[i]} {'=' * line_length}")

            best_rank = 7463  # rank one worse than worst hand todo why one worse
            winners = []

            for player, hand in enumerate(hands):
                # evaluate current board position
                rank = self.evaluate(hand, board[:(i + 3)])
                rank_class = self.get_rank_class(rank)
                class_string = self.class_to_string(rank_class)
                percentage = self.get_five_card_rank_percentage(rank)
                print(f"Player {player + 1} hand = {class_string}, percentage = {percentage}")

                # detect winner
                if rank == best_rank:
                    winners.append(player)
                    best_rank = rank
                elif rank < best_rank:
                    winners = [player]
                    best_rank = rank

            # if we're not on the river
            if stages[i] != "RIVER":
                if len(winners) == 1:
                    print(f"Player {winners[0] + 1} hand is currently winning")
                else:
                    winners_formatted = [w + 1 for w in winners]
                    print(f"Players {winners_formatted} are tied")

            # otherwise on all other streets
            else:
                print("=" * line_length) + " HAND OVER " + ("=" * line_length)
                winning_class_str = self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board)))
                if len(winners) == 1:
                    print(f"Player {winners[0] + 1} wins with a {winning_class_str}")

                else:
                    winners_formatted = [w + 1 for w in winners]
                    print(f"Players {winners_formatted} win with a {winning_class_str}")
