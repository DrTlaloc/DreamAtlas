from . import *


class Nation:

    def __init__(self, nation_data):

        # The nation index is used to lookup all the other properties of a nation from the .__init__ constants
        self.index, self.team = nation_data

        # Nation info
        for entry in ALL_NATIONS:
            if entry[0] == self.index:
                self.name = entry[1]
                self.tagline = entry[2]

        # Nation homeland config
        for entry in HOMELANDS_INFO:
            if entry[0] == self.index:
                self.terrain_profile = entry[1]
                self.layout = entry[2]
                self.cap_terrain = entry[3]
                self.home_plane = entry[4]

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string


# Info to build UI dynamically frames, buttons, [attribute, type, widget, label, options]
UI_CONFIG_CUSTOMNATION = {
    'label_frames': [
        ['Nation info', 0],
        ['Homeland info', 1]],
    'buttons': [1, 5, 6],
    'attributes': {
        'index': [int, 0, 'Nation Number', None, 1],
        'team': [int, 0, 'Team', None, 1],
        'name': [str, 0, 'Name', None, 1],
        'tagline': [str, 0, 'Tagline', None, 1],
        'cap_terrain': [int, 0, 'Capital Terrain', None, 1],

        'terrain_profile': [int, 1, 'Terrain Preference', ['Balanced', 'Plains', 'Forest', 'Mountains', 'Desert', 'Swamp', 'Karst'], 1],
        'layout': [int, 1, 'Layout', ['Land', 'Cave', 'Coast', 'Island', 'Deeps', 'Shallows', 'Lakes'], 1],
        'home_plane': [int, 1, 'Home Plane', ['Surface', 'Underground'], 1]
    }
}


class CustomNation:

    def __init__(self, custom_nation_data):
        self.index, self.name, self.tagline, terrain_index, layout_index, self.cap_terrain, self.home_plane, self.team = custom_nation_data
        self.terrain_profile = TERRAIN_PREFERENCES[terrain_index]
        self.layout = LAYOUT_PREFERENCES[layout_index]

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string


# Info to build UI dynamically frames, buttons, [attribute, type, widget, label, options]
UI_CONFIG_GENERICNATION = {
    'label_frames': [
        ['Info', 1]],
    'buttons': [1, 5, 6],
    'attributes': {
        'terrain_profile': [int, 1, 'Terrain Preference', ['Balanced', 'Plains', 'Forest', 'Mountains', 'Desert', 'Swamp', 'Karst'], 1],
        'layout': [int, 1, 'Layout', ['Land', 'Cave', 'Coast', 'Island', 'Deeps', 'Shallows', 'Lakes'], 1],
        'home_plane': [int, 1, 'Home Plane', ['Surface', 'Underground'], 1]
    }
}


class GenericNation:

    def __init__(self, generic_nation_data):
        terrain_index, layout_index, self.cap_terrain, self.home_plane = generic_nation_data
        self.terrain_profile = TERRAIN_PREFERENCES[terrain_index]
        self.layout = LAYOUT_PREFERENCES[layout_index]

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
