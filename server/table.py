from server_util import *
from player import Player
from table_handler_thread import TableHandlerThread
from base_game import BaseGame
from connected_client import ConnectedClient


class Table:
    MIN_PLAYERS = 2

    def __init__(self, server):
        self.server = server
        self.name = f"{len(server.tables) + 1}"
        self.events = Queue()
        self.game: BaseGame = server.get_default_game()(table=self)
        self.n_seats = 10
        self.seats_players = dict.fromkeys(range(1, self.n_seats + 1))

        TableHandlerThread(self).start()

        Log.info(f"Created table {self}")

    def __repr__(self):
        return f"<Table '{self.name}', {self.n_taken_seats()}/{self.n_total_seats()} players>"

    def __str__(self):
        return f"'{self.name}'"

    def add_bot(self, seat=None) -> int:
        bot_player = Player(bot_number=self.server.get_next_bot_number())
        seat = self.add_player(bot_player, seat)
        return seat

    def add_bots(self, amount=1):
        added_bots = 0

        seats = []
        for _ in range(amount):
            seat = self.add_bot()
            if seat:
                seats.append(seat)
                added_bots += 1

        Log.info(f"Added {added_bots}/{amount} bots to seats {seats}")

    def add_player(self, client_or_bot, seat=None) -> int:
        """sets and returns player's seat, 0 or AssertionError if fail"""

        if self.game.running:
            Log.warn("Can't add player: game running")  # todo add to a queue to join next round
            return 0

        assert client_or_bot, "no player given"

        if isinstance(client_or_bot, ConnectedClient):
            assert client_or_bot.player, "Client is not logged in"
            player = client_or_bot.player

        else:
            assert client_or_bot.is_bot, "Neither connected client nor bot player provided"
            player = client_or_bot

        empty_seats = self.get_empty_seats()

        if not empty_seats:
            Log.warn("No seats empty, ignoring call")
            return 0

        if seat:
            if seat in empty_seats:
                Log.trace(f"Given seat {seat} is available")
            else:
                Log.warn(f"Given seat {seat} is taken, choosing random seat")
                seat = random.choice(empty_seats)

        else:
            seat = random.choice(empty_seats)
            Log.trace(f"No seat given, chose random seat {seat}")

        self.put_player_in_seat(player, seat)
        self.events.put("player_added")
        return seat

    def get_empty_seats(self) -> list:
        empty_seats = []

        for seat, player in self.seats_players.items():
            if player is None:
                empty_seats.append(seat)

        return empty_seats

    def get_taken_seats(self) -> list:
        taken_seats = []

        for seat, player in self.seats_players.items():
            if player:
                taken_seats.append(seat)

        return taken_seats

    def get_taken_seats_players(self) -> dict:
        taken_seats_players = {}

        for seat, player in self.seats_players.items():
            if player:
                taken_seats_players[seat] = player

        return taken_seats_players

    def n_empty_seats(self) -> int:
        return len(self.get_empty_seats())

    def n_taken_seats(self) -> int:
        return len(self.get_taken_seats())

    def n_total_seats(self) -> int:
        total_seats = len(self.seats_players.items())
        return total_seats

    def put_player_in_seat(self, player: Player, seat: int):
        player["seat"] = seat
        self.seats_players[seat] = player  # todo should just be a list of participating_players
        Log.info(f"Put player {player} in seat {seat}")

    def send_player(self, target_player: dict, packet):
        for connection, player in self.server.connections_players:
            if player == target_player:
                self.server.send_single(connection, packet)

    def send_players(self, packet):
        for _, target_player in self.get_taken_seats_players().items():
            self.send_player(target_player, packet)

    def try_to_start_game(self):
        Log.info(f"Trying to start game")

        if self.game.running:
            Log.info("Game already started")
            return

        if self.n_taken_seats() < Table.MIN_PLAYERS:
            Log.info(f"Not enough players to start: {self.n_taken_seats()}/{self.MIN_PLAYERS}")
            return

        try:
            self.game.start()

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on game start", ex)
