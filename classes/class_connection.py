from . import *

# Info to build UI dynamically [attribute, type, widget, label, options, active]
UI_CONFIG_CONNECTION = {
    'label_frames': [['Connected Provinces', 0], ['Connection Type', 0]],
    'buttons': [0, 5],
    'attributes': {
        'connected_provinces': [tuple[int, int], 0, 'Connected Provinces', None, 0],
        'connection_int': [int, 6, 'Connection Type', None, 1]
    }
}


class Connection:

    def __init__(self,
                 connected_provinces: tuple[int, int] = (-1, -1),
                 connection_int: int = 0):

        # Graph data
        self.connected_provinces = connected_provinces
        self.connection_int = connection_int

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
