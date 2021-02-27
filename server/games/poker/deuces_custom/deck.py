from server_util import *

from .card import Card


FULL_DECK = [Card.new(rank + suit) for rank in Card.STR_RANKS for suit in Card.CHAR_SUIT_TO_INT_SUIT.keys()]


class Deck:
    def __init__(self):
        self.cards = FULL_DECK.copy()

    def shuffle(self):
        random.shuffle(self.cards)
        Log.trace("Deck shuffled")

    def draw(self, n_cards=1) -> List[Card]:  # exhaustive
        assert n_cards >= 1, "n_cards must be >= 1"

        cards_left = n_cards
        drawn_cards = []
        while cards_left:
            drawn_cards.append(self.cards.pop())
            cards_left -= 1

        Log.trace(f"Drawn {n_cards} card(s): {Card.get_pretty_str(drawn_cards)}")
        return drawn_cards

    def __str__(self):
        return Card.get_pretty_str(self.cards)
