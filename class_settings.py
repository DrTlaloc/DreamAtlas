# Imports all the DreamAtlas functionality and dependencies
from . import *


class DreamAtlasSettings:

    def __init__(self, index, map_title=None, wraparound=None, art_style=None, variance=None, pop_balancing=None,
                 site_frequency=None, water_province_size=None, cap_connections=None, homeland_size=None,
                 periphery_size=None, throne_count=None, player_neighbours=None, nations=None, seed=None, age=None):

        # General settings
        self.index = index
        if seed is None:
            seed = 1
        self.seed = seed
        if map_title is None:
            map_title = 'DreamAtlas_%i' % self.index
        self.map_title = map_title
        if wraparound is None:
            wraparound = 0
        self.wraparound = wraparound
        if art_style is None:
            art_style = 0
        self.art_style = art_style

        # Balance/flavour settings
        if variance is None:
            variance = 0.5
        self.variance = variance
        if pop_balancing is None:
            pop_balancing = 0
        self.pop_balancing = pop_balancing
        if site_frequency is None:
            site_frequency = 60
        self.site_frequency = site_frequency
        if water_province_size is None:
            water_province_size = 2
        self.water_province_size = water_province_size
        if cap_connections is None:
            cap_connections = 5
        self.cap_connections = cap_connections
        if homeland_size is None:
            homeland_size = 10
        self.homeland_size = homeland_size
        if periphery_size is None:
            periphery_size = 3
        self.periphery_size = periphery_size
        if throne_count is None:
            throne_count = 10
        self.throne_count = throne_count
        if player_neighbours is None:
            player_neighbours = 4
        self.player_neighbours = player_neighbours

        # Info about nations/age
        if nations is None:
            nations = []
        self.nations = nations
        if age is None:
            age = 2
        self.age = age

        # Constants defined by the previous settings
        self.spread = variance
        self.base_radius = 0.5

    def read_settings_file(self, filename):

        f = open(filename, 'r')
        lines = f.readlines()

        for line in lines:
            if line[0] != '#':
                continue

            line = line.split()

            if line[0] == '#seed':
                self.seed = line[1]
            if line[0] == '#map_title':
                self.map_title = line[1]
            if line[0] == '#wraparound':
                self.wraparound = int(line[1])
            if line[0] == '#art_style':
                self.art_style = int(line[1])

            if line[0] == '#variance':
                self.variance = float(line[1])
            if line[0] == '#pop_balancing':
                self.pop_balancing = int(line[1])
            if line[0] == '#site_frequency':
                self.site_frequency = int(line[1])
            if line[0] == '#water_province_size':
                self.water_province_size = float(line[1])
            if line[0] == '#cap_connections':
                self.cap_connections = int(line[1])
            if line[0] == '#homeland_size':
                self.homeland_size = int(line[1])
            if line[0] == '#periphery_size':
                self.periphery_size = int(line[1])
            if line[0] == '#throne_count':
                self.throne_count = int(line[1])
            if line[0] == '#player_neighbours':
                self.player_neighbours = int(line[1])
            if line[0] == '#nation':
                self.nations.append(int(line[1]))
            if line[0] == '#age':
                self.age = int(line[1])

        f.close()
