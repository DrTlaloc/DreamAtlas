from . import *


class Province:

    def __init__(self,
                 index: int = None,
                 plane: int = None,
                 coordinates: list = None,
                 fixed: bool = False,
                 terrain_int: int = 0,
                 capital_location: bool = False,
                 capital_nation: int = None,
                 parent_region: int = None,
                 has_commands: bool = False,
                 poptype: int = None,
                 owner: int = None,
                 killfeatures: bool = False,
                 features: list[int] = [],
                 knownfeatures: list[int] = [],
                 fort: int = None,
                 temple: bool = False,
                 lab: bool = False,
                 unrest: int = None,
                 population: int = None,
                 defence: int = None,
                 skybox: str = None,
                 batmap: str = None,
                 groundcol: list[int, int, int] = None,
                 rockcol: list[int, int, int] = None,
                 fogcol: list[int, int, int] = None,
                 size: float = None,
                 shape: float = None,
                 height: int = None):

        # Graph data
        self.index = index
        self.plane = plane
        self.coordinates = coordinates
        self.fixed = fixed

        # Province properties
        self.terrain_int = terrain_int
        self.capital_location = capital_location
        self.capital_nation = capital_nation
        self.parent_region = parent_region

        # Province commands
        self.has_commands = has_commands
        self.poptype = poptype
        self.owner = owner
        self.killfeatures = killfeatures
        self.features = features
        self.knownfeatures = knownfeatures
        self.fort = fort
        self.temple = temple
        self.lab = lab
        self.unrest = unrest
        self.population = population
        self.defence = defence
        self.skybox = skybox
        self.batmap = batmap
        self.groundcol = groundcol
        self.rockcol = rockcol
        self.fogcol = fogcol

        # Drawing properties
        self.size = size
        self.shape = shape
        self.height = height
