from server_util import *
from .card import Card


class LookupTable:
    """
    Number of Distinct Hand Values:
    Straight Flush   10
    Four of a Kind   156      [(13 choose 2) * (2 choose 1)]
    Full Houses      156      [(13 choose 2) * (2 choose 1)]
    Flush            1277     [(13 choose 5) - 10 straight flushes]
    Straight         10
    Three of a Kind  858      [(13 choose 3) * (3 choose 1)]
    Two Pair         858      [(13 choose 3) * (3 choose 2)]
    One Pair         2860     [(13 choose 4) * (4 choose 1)]
    High Card      + 1277     [(13 choose 5) - 10 straights]
    -------------------------
    TOTAL            7462
    Here we create a lookup table which maps:
        5 card hand's unique prime product => rank in range [1, 7462]
    Examples:
    * Royal flush (best hand possible)          => 1
    * 7-5-4-3-2 unsuited (worst hand possible)  => 7462
    """

    MAX_ROYAL_FLUSH = 1
    MAX_STRAIGHT_FLUSH = 10
    MAX_FOUR_OF_A_KIND = 166
    MAX_FULL_HOUSE = 322
    MAX_FLUSH = 1599
    MAX_STRAIGHT = 1609
    MAX_THREE_OF_A_KIND = 2467
    MAX_TWO_PAIR = 3325
    MAX_PAIR = 6185
    MAX_HIGH_CARD = 7462

    MAX_RANK_TO_STRING = {
        MAX_ROYAL_FLUSH: "Royal Flush",
        MAX_STRAIGHT_FLUSH: "Straight Flush",
        MAX_FOUR_OF_A_KIND: "Four of a Kind",
        MAX_FULL_HOUSE: "Full House",
        MAX_FLUSH: "Flush",
        MAX_STRAIGHT: "Straight",
        MAX_THREE_OF_A_KIND: "Three of a Kind",
        MAX_TWO_PAIR: "Two Pair",
        MAX_PAIR: "Pair",
        MAX_HIGH_CARD: "High Card"
    }

    def __init__(self):
        """
        Calculates lookup tables
        """

        # create dictionaries
        self.flush_lookup = {}
        self.unsuited_lookup = {}

        # create the lookup table in piecewise fashion
        self.flushes()  # this will call straights and high cards method,
        # we reuse some of the bit sequences
        self.multiples()

    def flushes(self):
        """
        Straight flushes and flushes.
        Lookup is done on 13 bit integer (2^13 > 7462):
        xxxbbbbb bbbbbbbb => integer hand index (bitrank)
        """

        # straight flushes in rank order
        straight_flushes = [
            7936,  # 0b11111_00000000, # royal flush
            3968,  # 0b1111_10000000,
            1984,  # 0b111_11000000,
            992,  # 0b11_11100000,
            496,  # 0b1_11110000,
            248,  # 0b11111000,
            124,  # 0b1111100,
            62,  # 0b111110,
            31,  # 0b11111,
            4111  # 0b10000_00001111 # 5 high
        ]

        # now we'll dynamically generate all the other
        # flushes (including straight flushes)
        flushes = []
        gen = self.get_lexographically_next_bit_sequence(0b11111)

        # 1277 = number of high cards
        # 1277 + len(str_flushes) is number of hands with all cards unique rank
        for i in range(1277 + len(straight_flushes) - 1):  # we also iterate over SFs
            # pull the next flush pattern from our generator
            f = next(gen)

            # if this flush matches perfectly any
            # straight flush, do not add it
            not_sf = True
            for sf in straight_flushes:
                # if f XOR sf == 0, then bit pattern
                # is same, and we should not add
                if not f ^ sf:
                    not_sf = False

            if not_sf:
                flushes.append(f)

        # we started from the lowest straight pattern, now we want to start ranking from
        # the most powerful hands, so we reverse
        flushes.reverse()

        # now add to the lookup map:
        # start with straight flushes and the rank of 1
        # since it is the best hand in poker
        # rank 1 = Royal Flush!
        rank = 1
        for sf in straight_flushes:
            prime_product = Card.prime_product_from_rankbits(sf)
            self.flush_lookup[prime_product] = rank
            rank += 1

        # we start the counting for flushes on max full house, which
        # is the worst rank that a full house can have (2,2,2,3,3)
        rank = LookupTable.MAX_FULL_HOUSE + 1
        for f in flushes:
            prime_product = Card.prime_product_from_rankbits(f)
            self.flush_lookup[prime_product] = rank
            rank += 1

        # we can reuse these bit sequences for straights
        # and high cards since they are inherently related
        # and differ only by context
        self.straight_and_high_cards(straight_flushes, flushes)

    def straight_and_high_cards(self, straights, high_cards):
        """
        Unique five card sets. Straights and high cards.
        Reuses bit sequences from flush calculations.
        """

        rank = LookupTable.MAX_FLUSH + 1
        for s in straights:
            prime_product = Card.prime_product_from_rankbits(s)
            self.unsuited_lookup[prime_product] = rank
            rank += 1

        rank = LookupTable.MAX_PAIR + 1
        for h in high_cards:
            prime_product = Card.prime_product_from_rankbits(h)
            self.unsuited_lookup[prime_product] = rank
            rank += 1

    def multiples(self):
        """
        Pair, Two Pair, Three of a Kind, Full House, and 4 of a Kind.
        """

        backwards_ranks = Card.INT_RANKS_REVERSED

        # 1) Four of a Kind
        rank = LookupTable.MAX_STRAIGHT_FLUSH + 1
        # for each choice of a set of four rank
        for i in backwards_ranks:
            # and for each possible kicker rank
            kickers = backwards_ranks[:]
            kickers.remove(i)
            for k in kickers:
                product = Card.PRIMES[i] ** 4 * Card.PRIMES[k]
                self.unsuited_lookup[product] = rank
                rank += 1

        # 2) Full House
        rank = LookupTable.MAX_FOUR_OF_A_KIND + 1
        # for each three of a kind
        for i in backwards_ranks:
            # and for each choice of pair rank
            pair_ranks = backwards_ranks[:]
            pair_ranks.remove(i)
            for pr in pair_ranks:
                product = Card.PRIMES[i] ** 3 * Card.PRIMES[pr] ** 2
                self.unsuited_lookup[product] = rank
                rank += 1

        # 3) Three of a Kind
        rank = LookupTable.MAX_STRAIGHT + 1
        # pick three of one rank
        for r in backwards_ranks:
            kickers = backwards_ranks[:]
            kickers.remove(r)
            gen = itertools.combinations(kickers, 2)

            for kickers in gen:
                c1, c2 = kickers
                product = Card.PRIMES[r] ** 3 * Card.PRIMES[c1] * Card.PRIMES[c2]
                self.unsuited_lookup[product] = rank
                rank += 1

        # 4) Two Pair
        rank = LookupTable.MAX_THREE_OF_A_KIND + 1
        tp_gen = itertools.combinations(backwards_ranks, 2)
        for tp in tp_gen:
            pair1, pair2 = tp
            kickers = backwards_ranks[:]
            kickers.remove(pair1)
            kickers.remove(pair2)
            for kicker in kickers:
                product = Card.PRIMES[pair1] ** 2 * Card.PRIMES[pair2] ** 2 * Card.PRIMES[kicker]
                self.unsuited_lookup[product] = rank
                rank += 1

        # 5) Pair
        rank = LookupTable.MAX_TWO_PAIR + 1
        # choose a pair
        for pair_rank in backwards_ranks:
            kickers = backwards_ranks.copy()
            kickers.remove(pair_rank)
            k_gen = itertools.combinations(kickers, 3)

            for kickers in k_gen:
                k1, k2, k3 = kickers
                product = Card.PRIMES[pair_rank] ** 2 * Card.PRIMES[k1] * \
                    Card.PRIMES[k2] * Card.PRIMES[k3]
                self.unsuited_lookup[product] = rank
                rank += 1

    @staticmethod
    def get_lexographically_next_bit_sequence(bits):
        """
        Bit hack from here:
        # http://www-graphics.stanford.edu/~seander/bithacks.html#NextBitPermutation
        Generator even does this in poker order rank
        so no need to sort when done! Perfect.
        """

        # what
        t = (bits | (bits - 1)) + 1
        next_bit_sequence = t | ((int((t & -t) / (bits & -bits)) >> 1) - 1)
        yield next_bit_sequence

        while True:
            t = (next_bit_sequence | (next_bit_sequence - 1)) + 1
            next_bit_sequence = t | ((int((t & -t) / (next_bit_sequence & -next_bit_sequence)) >> 1) - 1)
            yield next_bit_sequence

    @staticmethod
    def rank_to_percentile(hand_rank):
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """

        return hand_rank / LookupTable.MAX_HIGH_CARD

    @staticmethod
    def rank_to_string(hand_rank) -> str:
        """
        Gets the readable string correlated with the hand rank
        """

        if hand_rank == 1:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_ROYAL_FLUSH]
        if hand_rank <= LookupTable.MAX_STRAIGHT_FLUSH:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_STRAIGHT_FLUSH]
        if hand_rank <= LookupTable.MAX_FOUR_OF_A_KIND:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_FOUR_OF_A_KIND]
        if hand_rank <= LookupTable.MAX_FULL_HOUSE:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_FULL_HOUSE]
        if hand_rank <= LookupTable.MAX_FLUSH:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_FLUSH]
        if hand_rank <= LookupTable.MAX_STRAIGHT:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_STRAIGHT]
        if hand_rank <= LookupTable.MAX_THREE_OF_A_KIND:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_THREE_OF_A_KIND]
        if hand_rank <= LookupTable.MAX_TWO_PAIR:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_TWO_PAIR]
        if hand_rank <= LookupTable.MAX_PAIR:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_PAIR]
        if hand_rank <= LookupTable.MAX_HIGH_CARD:
            return LookupTable.MAX_RANK_TO_STRING[LookupTable.MAX_HIGH_CARD]

        raise ValueError(f"Invalid hand rank {hand_rank}")  # todo handle this ex
