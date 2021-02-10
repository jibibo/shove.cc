from util_server import *

from .card import Card


FULL_DECK = []
for suit in Card.CHAR_SUIT_TO_INT_SUIT.keys():
    for rank in Card.STR_RANKS:
        FULL_DECK.append(Card.new(rank + suit))


class Deck:
    """
    Class representing a deck. The first time we create, we seed the static
    deck with the list of unique card integers. Each object instantiated simply
    makes a copy of this object and shuffles it. todo not completely true anymore
    """

    def __init__(self):
        self.cards = FULL_DECK.copy()
        self.shuffle()

        log("Deck init done")

    def shuffle(self):
        random.shuffle(self.cards)
        log("Deck shuffled")

    def draw(self, n_cards=1) -> list:  # exhaustive
        assert n_cards >= 1, "n_cards must be >= 1"

        if n_cards == 1:
            return [self.cards.pop(0)]

        drawn_cards = []
        for i in range(n_cards):
            drawn_cards.extend(self.draw())

        log(f"Drawn cards: {Card.get_pretty_str(drawn_cards)}")
        return drawn_cards

    def __str__(self):
        return Card.get_pretty_str(self.cards)
