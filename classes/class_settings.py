from . import *


class DreamAtlasSettings:

    def __init__(self,
                 index: int,
                 map_title: str = None,
                 wraparound: tuple[bool, bool] = None,
                 art_style: int = None,
                 variance: float = None,
                 pop_balancing: int = None,
                 site_frequency: int = None,
                 water_province_size: float = None,
                 cave_province_size: float = None,
                 cap_connections: int = None,
                 homeland_size: int = None,
                 periphery_size: int = None,
                 throne_count: int = None,
                 player_neighbours: int = None,
                 nations: list[int, ...] = None,
                 custom_nations: list[list[int, int, int, int, int], ...] = None,
                 age: int = None,
                 seed: int = None):

        # General settings
        self.index = index
        if seed is None:
            seed = 1
        if map_title is None:
            map_title = 'DreamAtlas_%i' % self.index
        if wraparound is None:
            wraparound = 0
        if art_style is None:
            art_style = 0

        self.seed = seed
        self.map_title = map_title
        self.wraparound = wraparound
        self.art_style = art_style

        # Balance/flavour settings
        if variance is None:
            variance = 0.5
        if pop_balancing is None:
            pop_balancing = 0
        if site_frequency is None:
            site_frequency = 60
        if water_province_size is None:
            water_province_size = 2
        if cave_province_size is None:
            cave_province_size = 1.5
        if cap_connections is None:
            cap_connections = 5
        if homeland_size is None:
            homeland_size = 10
        if periphery_size is None:
            periphery_size = 3
        if throne_count is None:
            throne_count = 10
        if player_neighbours is None:
            player_neighbours = 4
            
        self.variance = variance
        self.pop_balancing = pop_balancing
        self.site_frequency = site_frequency
        self.water_province_size = water_province_size
        self.cave_province_size = cave_province_size
        self.cap_connections = cap_connections
        self.homeland_size = homeland_size
        self.periphery_size = periphery_size            
        self.throne_count = throne_count
        self.player_neighbours = player_neighbours

        # Info about nations/age
        if nations is None:
            nations = []
        if custom_nations is None:
            custom_nations = []
        if age is None:
            age = 2
            
        self.nations = nations
        self.custom_nations = custom_nations
        self.age = age
        self.base_radius = 0.5

    def read_settings_file(self, filename):

        with open(filename, 'r') as f:
            for _ in f.readlines():
                if _[0] != '#':
                    continue

                _ = _.split()

                if _[0] == '#seed':
                    self.seed = _[1]
                if _[0] == '#map_title':
                    self.map_title = _[1]
                if _[0] == '#wraparound':
                    self.wraparound = int(_[1])
                if _[0] == '#art_style':
                    self.art_style = int(_[1])

                if _[0] == '#variance':
                    self.variance = float(_[1])
                if _[0] == '#pop_balancing':
                    self.pop_balancing = int(_[1])
                if _[0] == '#site_frequency':
                    self.site_frequency = int(_[1])
                if _[0] == '#water_province_size':
                    self.water_province_size = float(_[1])
                if _[0] == '#cave_province_size':
                    self.cave_province_size = float(_[1])
                if _[0] == '#cap_connections':
                    self.cap_connections = int(_[1])
                if _[0] == '#homeland_size':
                    self.homeland_size = int(_[1])
                if _[0] == '#periphery_size':
                    self.periphery_size = int(_[1])
                if _[0] == '#throne_count':
                    self.throne_count = int(_[1])
                if _[0] == '#player_neighbours':
                    self.player_neighbours = int(_[1])
                if _[0] == '#nation':
                    self.nations.append(int(_[1]))
                if _[0] == '#age':
                    self.age = int(_[1])
