from src.convenience import *

from .card import Card


FULL_DECK = [Card.from_str(rank + suit) for rank in Card.RANKS_INT_TO_RANK_CHAR for suit in Card.SUIT_CHAR_TO_SUIT_INT.keys()]


class Deck:
    def __init__(self):
        self.cards = FULL_DECK.copy()

    def __str__(self):
        return Card.get_pretty_str(self.cards)

    def deal_players(self, players):
        Log.trace("Dealing cards to players")

        for player in players:
            drawn_cards = self.draw(2)
            player["cards"] = drawn_cards
            Log.debug(f"Dealt cards to {player}: {Card.get_pretty_str(drawn_cards)}")

        Log.info("Dealt cards to players")

    def draw(self, n_cards=1) -> List[int]:  # exhaustive
        assert n_cards >= 1, "n_cards must be >= 1"

        cards_left = n_cards
        drawn_cards = []
        while cards_left:
            card = self.cards.pop()
            drawn_cards.append(card)
            cards_left -= 1

        Log.trace(f"Drawn {n_cards} card(s) from deck: {Card.get_pretty_str(drawn_cards)}")
        return drawn_cards

    def shuffle(self):
        random.shuffle(self.cards)
        Log.trace("Deck shuffled")
