# Imports all the DreamAtlas functionality and dependencies
from . import *


class Nation:

    def __init__(self, nation_index):

        # The nation index is used to lookup all the other properties of a nation from the .__init__ constants
        self.index = nation_index

        # Nation info
        for entry in ALL_NATIONS:
            if entry[0] == self.index:
                self.name = entry[1]
                self.tagline = entry[2]

        # Nation homeland settings
        for entry in HOMELANDS_INFO:
            if entry[0] == self.index:
                self.terrain_profile = entry[1]
                self.layout = entry[2]
                self.cap_terrain = entry[3]
                self.home_plane = entry[4]
