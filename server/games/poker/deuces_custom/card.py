class Card:  # todo can easily be made OOP
    """
    Static class that handles cards. We represent cards as 32-bit integers, so
    there is no object instantiation - they are just ints. Most of the bits are
    used, and have a specific meaning. See below:
                                    Card:
                            bitrank   suit rank   prime
                    +--------+--------+--------+--------+
                    |xxxbbbbb bbbbbbbb|cdhsrrrr|xxpppppp|
                    +--------+--------+--------+--------+
        1) p = prime number of rank (deuce=2,trey=3,four=5,...,ace=41)
        2) r = rank of card (deuce=0,trey=1,four=2,five=3,...,ace=12)
        3) cdhs = suit of card (bit turned on based on suit of card)
        4) b = bit turned on depending on rank of card
        5) x = unused
    This representation will allow us to do very important things like:
    - Make a unique prime product for each hand
    - Detect flushes
    - Detect straights
    and is also quite performant.
    """

    STR_RANKS = list("23456789TJQKA")
    INT_RANKS = list(range(13))
    INT_RANKS_REVERSED = INT_RANKS
    INT_RANKS_REVERSED.reverse()
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

    CHAR_RANK_TO_INT_RANK = dict(zip(STR_RANKS, INT_RANKS))
    CHAR_SUIT_TO_INT_SUIT = {
        "s": 1,
        "h": 2,
        "d": 4,
        "c": 8
    }
    INT_SUIT_TO_CHAR_SUIT = list("xshxdxxxc")
    PRETTY_SUITS = {
        1: chr(9824),  # spades
        2: chr(9829),  # hearts
        4: chr(9830),  # diamonds
        8: chr(9827)  # clubs
    }

    @staticmethod
    def get_bitrank_int(card_int):
        return (card_int >> 16) & 0b11111_11111111

    @staticmethod
    def get_prime(card_int):
        return card_int & 0b111111

    @staticmethod
    def get_rank_int(card_int):
        return (card_int >> 8) & 0b1111

    @staticmethod
    def get_suit_int(card_int):
        return (card_int >> 12) & 0b1111

    @staticmethod
    def hand_to_bin(card_str_list):
        """
        Expects a list of cards as strings and returns a list
        of integers of same length corresponding to those strings.
        """

        card_bin_list = []
        for card_str in card_str_list:
            card_bin_list.append(Card.new(card_str))
        return card_bin_list

    @staticmethod
    def int_to_bin(card_int):
        """
        For debugging purposes. Displays the binary number as a
        human readable string in groups of four digits.
        """

        bin_str = bin(card_int)[2:][::-1]  # chop off the 0b and THEN reverse string
        output = list("\t".join(["0000"] * 8))

        for i in range(len(bin_str)):
            output[i + int(i / 4)] = bin_str[i]  # todo what

        # output the string to console
        output.reverse()
        return "".join(output)

    @staticmethod
    def int_to_pretty_str(card_int):
        """
        Prints a single card
        """

        # suit and rank
        suit_int = Card.get_suit_int(card_int)
        rank_int = Card.get_rank_int(card_int)

        # if we need to color red
        s = Card.PRETTY_SUITS[suit_int]
        r = Card.STR_RANKS[rank_int]

        return f"[{r}{s}]"

    @staticmethod
    def int_to_str(card_int):
        rank_int = Card.get_rank_int(card_int)
        suit_int = Card.get_suit_int(card_int)
        return Card.STR_RANKS[rank_int] + Card.INT_SUIT_TO_CHAR_SUIT[suit_int]

    @staticmethod
    def new(card_str):
        """
        Converts Card string to binary integer representation of card, inspired by:

        http://www.suffecool.net/poker/evaluator.html
        """

        # example: As
        rank_char = card_str[0]  # = A
        suit_char = card_str[1]  # = s
        rank_int = Card.CHAR_RANK_TO_INT_RANK[rank_char]  # = 12 = 0b1100
        suit_int = Card.CHAR_SUIT_TO_INT_SUIT[suit_char]  # = 1 = 0b0001
        rank_prime = Card.PRIMES[rank_int]  # = 41 = 0b00101001

        bitrank = 1 << rank_int << 16
        # 0b00000000 00000000 00000000 00000001 1
        # 0b00000000 00000000 00010000 00000000 << 12
        # 0b00010000 00000000 00000000 00000000 << 16
        suit = suit_int << 12
        # 0b00000000 00000000 00000000 00000001 1
        # 0b00000000 00000000 00010000 00000000 << 12
        rank = rank_int << 8
        # 0b00000000 00000000 00000000 00001100 12
        # 0b00000000 00000000 00001100 00000000 << 8

        return bitrank | suit | rank | rank_prime
        # example gives: 0b00010000 00000000 00011100 00101001

    @staticmethod
    def prime_product_from_hand(card_int_list):
        """
        Expects a list of cards in integer form.
        """

        product = 1
        for card_int in card_int_list:
            product *= (card_int & 0b11111111)

        return product

    @staticmethod
    def prime_product_from_rankbits(rankbits):
        """
        Returns the prime product using the bitrank (b)
        bits of the hand. Each 1 in the sequence is converted
        to the correct prime and multiplied in.
        Params:
            rankbits = a single 32-bit (only 13-bits set) integer representing
                    the ranks of 5 _different_ ranked cards
                    (5 of 13 bits are set)
        Primarily used for evaluating flushes and straights,
        two occasions where we know the ranks are *ALL* different.
        Assumes that the input is in form (set bits):
                              rankbits
                        +--------+--------+
                        |xxxbbbbb|bbbbbbbb|
                        +--------+--------+
        """

        product = 1
        for i in Card.INT_RANKS:
            # if the ith bit is set
            if rankbits & (1 << i):
                product *= Card.PRIMES[i]

        return product

    @staticmethod
    def print_pretty_card(card_int):  # todo should be removed
        """
        Expects a single integer as input
        """

        print(Card.int_to_pretty_str(card_int))

    @staticmethod
    def get_pretty_str(card_int_list):  # todo should be removed
        """
        Expects a list of cards in integer form.
        """

        # output = " "
        # for i in range(len(card_int_list)):
        #     c = card_int_list[i]
        #     if i != len(card_int_list) - 1:
        #         output += Card.int_to_pretty_str(c) + ","
        #     else:
        #         output += Card.int_to_pretty_str(c) + " "

        return " ".join([Card.int_to_pretty_str(card_int) for card_int in card_int_list])
