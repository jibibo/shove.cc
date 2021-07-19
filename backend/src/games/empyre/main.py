from convenience_empyre import *


class CitizenDied(Exception):
    pass


class CitizenStarving(Exception):
    pass


class CitizenUnemployed(Exception):
    pass


class Manager:
    def __init__(self):
        self.players = []

    def create_player(self, username):
        player = Player(username)
        self.players.append(player)
        return player

    def start_tick_thread(self):
        Thread(target=self.tick_thread, daemon=True).start()

    def tick_thread(self):
        while 1:
            time.sleep(3)
            for player in self.players:
                player.tick()


class Tickable:
    def __init__(self):
        self.age = 0

    def _inc_age(self):
        self.age += 1
        print(f"{repr(self)} ticked, age: {self.age}")

    def tick(self):
        pass


class Player(Tickable):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.worlds = [World(self) for _ in range(1)]
        print(f"{self} initialized")

    def __repr__(self):
        return f"<{type(self).__name__} {self.username}>"

    def tick(self):
        self._inc_age()
        for world in self.worlds:
            world.tick()


class World(Tickable):
    def __init__(self, player, size=10):
        super().__init__()
        self.player = player
        self.size = size
        self.tile_noise_dict = {}
        self.feature_noise_dict = {}
        self.tile_dict = {_: {} for _ in range(size)}
        self.buildings = []
        self.resources = {
            "food": 1,
            "wood": 1
        }
        self.generate_noise()
        self.char_dict = {  # 0-0.9 X 1-1.9 Y 2-2.9 Z
            0: Ocean,
            0.25: Coast,
            0.3: Grassland,
            0.45: Plains,
            0.65: Mountain,
            0.9: Snow,
        }
        self.init_tiles()
        self.citizens = [Citizen(self) for _ in range(1)]
        self.add_building(Palace, 0, 0)
        print(f"World initialized")

    def __repr__(self):
        return f"<World, resources: {self.resources}>"

    def __str__(self):
        formatted = "\n 0123456789\n"

        for y in range(self.size):
            formatted += str(y)
            for x in range(self.size):
                tile = self.tile_dict[x][y]

                if type(tile) in [Grassland, Plains] and \
                        tile.features:
                    symbol = tile.features[0].symbol
                else:
                    symbol = tile.symbol

                assert symbol, f"No symbol available for {tile}"

                formatted += symbol

            formatted += "\n"
        return f"Tiles: {formatted}"

    def tick(self):
        self._inc_age()

        for citizen in self.citizens:
            try:
                citizen.tick()
            except CitizenDied:
                print(f"{citizen} died, removing")
                self.citizens.remove(citizen)

        self.try_inc_population()

        for building in self.buildings:
            building.tick()

    def add_building(self, clazz, x, y):
        building = clazz(self, x, y)
        self.buildings.append(building)
        return building

    def get_n_citizens(self) -> len:
        return len(self.citizens)

    def generate_noise(self):
        tile_noise_generator = PerlinNoise(octaves=1.5, seed=None)
        feature_noise_generator = PerlinNoise(octaves=1, seed=None)
        print("Generating noise")
        tile_noise_dict = {}
        feature_noise_dict = {}
        for x in range(self.size):
            tile_noise_dict[x] = {}
            feature_noise_dict[x] = {}
            for y in range(self.size):
                tile_noise = float(
                    tile_noise_generator((x / self.size, y / self.size))
                ) + 0.5
                tile_noise_dict[x][y] = tile_noise
                feature_noise = float(
                    feature_noise_generator((x / self.size, y / self.size))
                ) + 0.5
                feature_noise_dict[x][y] = round(feature_noise, 1)

        self.tile_noise_dict = tile_noise_dict
        self.feature_noise_dict = feature_noise_dict
        print("Generated noise")

    def init_tiles(self):  # todo
        for x in range(self.size):
            for y in range(self.size):
                noise = self.tile_noise_dict[x][y]
                selected_class = None
                for threshold, clazz in self.char_dict.items():
                    if noise < threshold:
                        break
                    selected_class = clazz

                assert selected_class, f"No match with char_dict keys: {noise}, {selected_class}"
                tile = selected_class(self, x, y)

                if selected_class in [Plains, Grassland]:
                    if 0.4 < self.feature_noise_dict[x][y] < 0.7:
                        tile.features = [Hills(self, x, y)]
                    elif 0.7 < self.feature_noise_dict[x][y] < 1.0:
                        tile.features = [Forest(self, x, y)]

                self.tile_dict[x][y] = tile

    def try_inc_population(self):
        if self.resources["food"] > self.get_n_citizens() + 1:
            self.citizens.append(Citizen(self))
            print(f"Increased population to {self.get_n_citizens()}")


class Citizen(Tickable):
    def __init__(self, world):
        super().__init__()
        self.world = world
        self.starving_ticks = 0
        self.working_tile = None
        with open("names.json", "r") as f:
            data = json.load(f)
            self.name = random.choice(data["first"])
        print(f"{self} initialized")

    def __repr__(self):
        return f"<Citizen {self.name}>"

    def tick(self):
        self._inc_age()

        try:
            self.try_eat()

            if self.starving_ticks:
                self.starving_ticks = 0
                print(f"f{self}: no longer starving")

        except CitizenStarving:
            self.starving_ticks += 1
            print(f"{self}: no food available, starving")
            if self.starving_ticks == 3:
                raise CitizenDied

        try:
            self.do_work()

        except CitizenUnemployed:
            pass

    def do_work(self):  # todo
        if self.working_tile:
            pass

    def try_eat(self):
        food = self.world.resources["food"]
        if food < 1:
            raise CitizenStarving

        self.world.resources["food"] = food - 1


class Building(Tickable):
    def __init__(self, world, symbol, x, y):
        super().__init__()
        self.world = world
        self.symbol = symbol
        self.x = x
        self.y = y

    def __repr__(self):
        return f"<{type(self).__name__} at {self.x},{self.y}>"


class Palace(Building):
    def __init__(self, world, x, y):
        super().__init__(world, "P", x, y)
        print(f"{self} initialized")

    def tick(self):
        self._inc_age()


class Tile:
    symbol = "X"

    def __init__(self, world, base_yields, x, y):
        self.world = world
        self.base_yields = base_yields
        self.x = x
        self.y = y
        self.yields = {}  # todo compute on the go
        # self.production = 0
        # self.food = 0
        # self.gold = 0
        # self.science = 0
        # self.culture = 0
        # self.faith = 0
        # self.wood = 0
        # self.stone = 0
        # self.iron = 0
        self.features = None


class Coast(Tile):
    symbol = "~"

    def __init__(self, world, x, y):
        super().__init__(world, {
            "food": 1
        }, x, y)


class Grassland(Tile):
    symbol = "="

    def __init__(self, world, x, y):
        super().__init__(world, {
            "food": 2
        }, x, y)


class Mountain(Tile):
    symbol = "Ʌ"

    def __init__(self, world, x, y):
        super().__init__(world, {}, x, y)


class Ocean(Tile):
    symbol = "≈"

    def __init__(self, world, x, y):
        super().__init__(world, {
            "food": 1
        },  x, y)


class Plains(Tile):
    symbol = "-"

    def __init__(self, world, x, y):
        super().__init__(world, {
            "food": 1,
            "production": 1
        }, x, y)


class Snow(Tile):
    symbol = "*"

    def __init__(self, world, x, y):
        super().__init__(world, {}, x, y)


class TileFeature:
    def __init__(self, world, feature_yields, x, y):
        self.world = world
        self.feature_yields = feature_yields
        self.x = x
        self.y = y


class Forest(TileFeature):
    symbol = "f"

    def __init__(self, world, x, y):
        super().__init__(world, {
            "production": 1,
            "wood": 1
        }, x, y)


class Hills(TileFeature):
    symbol = "h"

    def __init__(self, world, x, y):
        super().__init__(world, {
            "production": 1,
            "stone": 1
        }, x, y)


def main():
    manager = Manager()
    manager.start_tick_thread()
    player = manager.create_player("user1")
    world = player.worlds[0]
    print(str(world))
    while 1:
        input_str = input()


if __name__ == "__main__":
    main()