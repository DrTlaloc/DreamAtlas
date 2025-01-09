
# Info to build UI dynamically [attribute, type, widget, label, options, active]
UI_CONFIG_PROVINCE = {
    'label_frames': [
        ['Province info', 0],
        ['Province info', 1],
        ['Province attributes', 3]],
    'buttons': [0, 5],
    'attributes': {
        'index': [int, 0, 'Province Number', None, 0],
        'name': [str, 0, 'Province Name', None, 1],
        'plane': [int, 0, 'Plane', None, 0],
        # 'coordinates': [list, 0, 'Coordinates', None, 0],
        'terrain_int': [int, 0, 'Terrain Integer', None, 1],
        'parent_region': [int, 0, 'Parent Region', None, 0],
        'unrest': [int, 0, 'Unrest', None, 0],
        'population': [int, 0, 'Population', None, 0],
        'defence': [int, 0, 'Defence', None, 0],

        'poptype': [int, 1, 'Poptype', ['Pops go here'], 0],
        'owner': [int, 1, 'Owner', ['Owners go here'], 0],
        'capital_nation': [int, 1, 'Nation Start', ['Natstart go here'], 0],
        # 'features' : [list, 1, 'Features', ['Features go here'], 0],
        # 'knownfeatures' : [list, 1, 'Revealed Features', ['Revealed features go here'], 0],
        'fort' : [int, 1, 'Fort', ['Fort go here'], 0],

        'capital_location': [int, 3, 'Capital Location Start', None, 0],
        'killfeatures': [int, 3, 'No features', None, 0],
        'temple': [int, 3, 'Temple', None, 0],
        'lab': [int, 3, 'Lab', None, 0],

    }
}


class Province:

    def __init__(self,
                 index: int = None,
                 name: str = None,
                 plane: int = None,
                 coordinates: list = None,
                 terrain_int: int = 0,
                 capital_location: bool = False,
                 capital_nation: int = None,
                 parent_region=None,
                 has_commands: bool = False,
                 poptype: int = None,
                 owner: int = None,
                 killfeatures: bool = False,
                 features: list[int] = list(),
                 knownfeatures: list[int] = list(),
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
        self.name = name
        self.plane = plane
        self.coordinates = coordinates

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

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
