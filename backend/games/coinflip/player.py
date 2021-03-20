# todo possibly also add a base_player abstract class that makes sure a "user" object is set?

class Player:
    def __init__(self, user, choice, bet):
        self.user = user
        self.choice = choice
        self.bet = bet
