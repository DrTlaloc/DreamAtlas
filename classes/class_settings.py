from . import *

# Info to build UI dynamically frames, buttons, [attribute, type, widget, label, options]
UI_CONFIG_SETTINGS = {
    'label_frames': [
        ['Map Info', 0],
        ['General Settings', 1],
        ['Map Sliders', 2],
        ['Additional Options', 3],
        ['Vanilla Nations', 4],
        ['Generic/Custom Nations', 5]],
    'buttons': [2, 3, 4, 5, 6],
    'attributes': {
        'map_title': [str, 0, 'Map Title', None, 1],
        'seed': [int, 0, 'Seed', None, 1],
        'description': [str, 0, 'Description', None, 1],

        'art_style': [int, 1, 'Art Style', ['.d6m'], 1],
        'age': [int, 1, 'Age', ['Early Age', 'Middle Age', 'Late Age'], 1],
        'wraparound': [int, 1, 'Wraparound', ['None', 'Horizontal', 'Vertical', 'Full'], 1],
        'pop_balancing': [int, 1, 'Population Balancing', ['Vanilla', 'Soft', 'Hard'], 1],
        'cave_type': [int, 1, 'Cave Type', ['Sparse', 'Tunnels', 'Caverns', 'Hollow Earth'], 0],
        'water_type': [int, 1, 'Underwater Type', ['Lakes', 'Seven Seas', 'Panthallassa'], 0],

        'cap_connections': [int, 2, 'Capital Connections', [3, 8], 1],
        'player_neighbours': [int, 2, 'Player Neighbours', [2, 7], 1],
        'homeland_size': [int, 2, 'Homeland Size', [4, 12], 1],
        'periphery_size': [int, 2, 'Periphery Size', [1, 8], 1],
        'throne_sites': [int, 2, 'Throne Sites', [4, 32], 1],
        'site_frequency': [int, 2, 'Site Frequency', [40, 100], 1],
        'water_province_value': [int, 2, 'Water Province Value %', [50, 200], 0],
        'water_province_percent': [int, 2, 'UW %', [0, 400], 0],
        'cave_province_value': [int, 2, 'Cave Province Value %', [50, 200], 0],
        'cave_province_percent': [int, 2, 'Cave %', [50, 400], 0],

        'disciples': [int, 3, 'Disciples', None, 0],
        'omniscience': [int, 3, 'Omniscience', None, 1],

        'nations': [list, 4, 'Vanilla Nations', None, 1],

        'custom_nations': [list, 5, 'Custom/Generic Nations', None, 1]
    }
}


class DreamAtlasSettings:

    def __init__(self, index: int):  # DreamAtlas generator settings

        self.index = index
        self.seed: int = 0
        self.description: str = None
        self.map_title: str = None
        self.art_style: int = None
        self.wraparound: int = None
        self.pop_balancing: int = None
        self.site_frequency: int = None
        self.water_province_value: float = None
        self.water_type: int = None
        self.water_province_percent: float = None
        self.cave_province_value: float = None
        self.cave_type: int = None
        self.cave_province_percent: float = None
        self.cap_connections: int = None
        self.homeland_size: int = None
        self.periphery_size: int = None
        self.throne_sites: int = None
        self.player_neighbours: int = None
        self.disciples: bool = False
        self.nations: list[list[int]] = list()
        self.custom_nations: list[list[int]] = list()
        self.generic_nations: list[list[int]] = list()
        self.age: int = None
        self.omniscience: bool = False

    def load_file(self, filename):

        self.__init__(self.index)  # Reset class

        with open(filename, 'r') as f:
            for _ in f.readlines():
                if _[0] == '#':  # Only do anything if the line starts with a command tag
                    _ = _.split()
                    attribute = _[0].strip('#')
                    if attribute == 'nation':
                        self.nations.append([int(_[1]), int(_[2])])
                    elif attribute == 'custom_nation':
                        self.custom_nations.append([int(_[1]), str(_[2]), str(_[3]), int(_[4]), int(_[5]), int(_[6]), int(_[7]), int(_[8])])
                    else:
                        attribute_type, widget, label, options, active = UI_CONFIG_SETTINGS['attributes'][attribute]
                        setattr(self, attribute, attribute_type(_[1]))  # Single entry

    def save_file(self, filename):

        with open(filename, 'w') as f:  # Writes all the settings to a file
            for attribute in self.__dict__:
                if attribute == 'nations':
                    for i in getattr(self, attribute):
                        f.write(f'#nation {i[0]} {i[1]}\n')
                elif attribute == 'custom_nations':
                    for i in getattr(self, attribute):
                        f.write(f'#customnation {i[0]} {i[1]}\n')
                else:
                    f.write(f'#{attribute} %{getattr(self, attribute)}\n')

    def __str__(self):

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
