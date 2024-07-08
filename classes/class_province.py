from . import *


class Province:

    def __init__(self,
                 index: int = None,
                 plane: int = None,
                 terrain_int: int = 0,
                 population: int = None,
                 capital_location: bool = False,
                 capital_nation: int = None,
                 parent_region: int = None,
                 coordinates: list = None,
                 size: float = None,
                 shape: float = None,
                 height: int = None):

        # Graph data
        self.index = index
        self.plane = plane
        self.coordinates = coordinates

        # Province properties
        self.terrain_int = terrain_int
        self.population = population
        self.capital_location = capital_location
        self.capital_nation = capital_nation
        self.parent_region = parent_region

        # Drawing properties
        self.size = size
        self.shape = shape
        self.height = height
