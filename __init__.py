import math
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy as sc
import scipy.spatial.distance as scd
from scipy.linalg import norm as scnorm
import random as rd
import minorminer as mnm
import minorminer.layout as mnml
import networkx as ntx
from pathlib import Path
import struct
from typing import Type

# Parallelization setup
from numba import jit, njit, prange
import numpy as np

# DOMINIONS DATA
########################################################################################################################

TERRAIN_DATA = [
    [None, 0, 'Plains'], [0, 1, 'Small Province'], [1, 2, 'Large Province'], [2, 4, 'Sea'],
    [3, 8, 'Freshwater'], [4, 16, 'Highlands (or gorge)'], [5, 32, 'Swamp'], [6, 64, 'Waste'],
    [7, 128, 'Forest (or kelp forest)'], [8, 256, 'Farm'], [9, 512, 'No start'], [10, 1024, 'Many Sites'],
    [11, 2048, 'Deep Sea'], [12, 4096, 'Cave'], [13, 8192, 'Fire sites'], [14, 16384, 'Air sites'],
    [15, 32768, 'Water sites'], [16, 65536, 'Earth sites'], [17, 131072, 'Astral sites'],
    [18, 262144, 'Death sites'], [19, 524288, 'Nature sites'], [20, 1048576, 'Glamour sites'],
    [21, 2097152, 'Blood sites'], [22, 4194304, 'Holy Sites'], [23, 8388608, 'Mountains'],
    [25, 33554432, 'Good throne location'], [26, 67108864, 'Good start location'],
    [27, 134217728, 'Bad throne location'],
    [30, 1073741824, 'Warmer'], [31, 2147483648, 'Colder'], [36, 68719476736, 'Cave Wall']
]

EA_NATIONS = [
    [5, 'Arcoscephale', 'Golden Era'], [6, 'Mekone', 'Brazen Giants'], [7, 'Pangaea', 'Age of Revelry'],
    [8, 'Ermor', 'New Faith'], [9, 'Sauromatia', 'Amazon Queens'], [10, 'Fomoria', 'The Cursed Ones'],
    [11, 'Tir na nog', 'Land of the Ever Young'], [12, 'Marverni', 'Time of Druids'], [13, 'Ulm', 'Enigma of Steel'],
    [14, 'Pyrene', 'Kingdom of the Bekrydes'], [15, 'Agartha', 'Pale Ones'], [16, 'Abysia', 'Children of Flame'],
    [17, 'Hinnom', 'Sons of the Fallen'], [18, 'Ubar', 'Kingdom of the Unseen'], [19, 'Ur The', 'First City'],
    [20, 'Kailasa', 'Rise of the Ape Kings'], [21, 'Lanka', 'Land of Demons'], [22, 'Tien Chi', 'Spring and Autumn'],
    [23, 'Yomi', 'Oni Kings'], [24, 'Caelum', 'Eagle Kings'], [25, 'Mictlan', 'Reign of Blood'],
    [26, 'Xibalba', 'Vigil of the Sun'], [27, 'Ctis', 'Lizard Kings'], [28, 'Machaka', 'Lion Kings'],
    [29, 'Berytos', 'Phoenix Empire'], [30, 'Vanheim', 'Age of Vanir'], [31, 'Helheim', 'Dusk and Death'],
    [32, 'Rus', 'Sons of Heaven'], [33, 'Niefelheim', 'Sons of Winter'], [34, 'Muspelheim', 'Sons of Fire'],
    [40, 'Pelagia', 'Pearl Kings'], [41, 'Oceania', 'Coming of the Capricorns'], [42, 'Therodos', 'Telkhine Spectre'],
    [43, 'Atlantis', 'Emergence of the Deep Ones'], [4, 'Rlyeh', 'Time of Aboleths']
]

MA_NATIONS = [
    [50, 'Arcoscephale', 'The Old Kingdom'], [51, 'Phlegra', 'Deformed Giants'], [52, 'Pangaea', 'Age of Bronze'],
    [53, 'Asphodel', 'Carrion Woods'], [54, 'Ermor', 'Ashen Empire'], [55, 'Sceleria', 'Reformed Empire'],
    [56, 'Pythium', 'Emerald Empire'], [57, 'Man', 'Tower of Avalon'], [58, 'Eriu', 'Last of the Tuatha'],
    [59, 'Agartha', 'Golem Cult'], [60, 'Ulm', 'Forges of Ulm'], [61, 'Marignon', 'Fiery Justice'],
    [62, 'Pyrene', 'Time of the Akelarre'], [63, 'Abysia', 'Blood and Fire'], [64, 'Ashdod', 'Reign of the Anakim'],
    [65, 'Naba', 'Queens of the Desert'], [66, 'Uruk', 'City States'],
    [67, 'Ind', 'Magnificent Kingdom of Exalted Virtue'],
    [68, 'Bandar Log', 'Land of the Apes'], [69, 'Tien Chi', 'Imperial Bureaucracy'],
    [70, 'Shinuyama', 'Land of the Bakemono'],
    [71, 'Caelum', 'Reign of the Seraphim'], [72, 'Nazca', 'Kingdom of the Sun'],
    [73, 'Mictlan', 'Reign of the Lawgiver'],
    [74, 'Xibalba', 'Flooded Caves'], [75, 'Ctis', 'Miasma'], [76, 'Machaka', 'Reign of Sorcerors'],
    [77, 'Phaeacia', 'Isle of the Dark Ships'], [78, 'Vanheim', 'Arrival of Man'], [79, 'Vanarus', 'Land of the Chuds'],
    [80, 'Jotunheim', 'Iron Woods'], [81, 'Nidavangr', 'Bear, Wolf and Crow'], [85, 'Ys', 'Morgen Queens'],
    [86, 'Pelagia', 'Triton Kings'], [87, 'Oceania', 'Mermidons'], [88, 'Atlantis', 'Kings of the Deep'],
    [89, 'Rlyeh', 'Fallen Star']
]

LA_NATIONS = [
    [95, 'Arcoscephale', 'Sibylline Guidance'], [96, 'Phlegra', 'Sleeping Giants'], [97, 'Pangaea', 'New Era'],
    [98, 'Pythium', 'Serpent Cult'], [99, 'Lemuria', 'Soul Gate'], [100, 'Man', 'Towers of Chelms'],
    [101, 'Ulm', 'Black Forest'], [102, 'Agartha', 'Ktonian Dead'], [103, 'Marignon', 'Conquerors of the Sea'],
    [104, 'Abysia', 'Blood of Humans'], [105, 'Ragha', 'Dual Kingdom'], [106, 'Caelum', 'Return of the Raptors'],
    [107, 'Gath', 'Last of the Giants'], [108, 'Patala', 'Reign of the Nagas'], [109, 'Tien Chi', 'Barbarian Kings'],
    [110, 'Jomon', 'Human Daimyos'], [111, 'Mictlan', 'Blood and Rain'], [112, 'Xibalba', 'Return of the Zotz'],
    [113, 'Ctis', 'Desert Tombs'], [115, 'Midgard', 'Age of Men'], [116, 'Bogarus', 'Age of Heroes'],
    [117, 'Utgard', 'Well of Urd'], [118, 'Vaettiheim', 'Wolf Kin Jarldom'], [119, 'Feminie', 'Sage-Queens'],
    [120, 'Piconye', 'Legacy of the Prester King'], [121, 'Andramania', 'Dog Republic'],
    [125, 'Erytheia', 'Kingdom of Two Worlds'], [106, 'Atlantis', 'Frozen Sea'], [107, 'Rlyeh', 'Dreamlands']
]

OTHER_NATIONS = [
    [0, 'Independents', 'Normal Independents'],
    [2, 'Special Independents', 'e.g. Horrors'],
    [4, 'Roaming Independents', 'e.g. Barbarians']
]

ALL_NATIONS = OTHER_NATIONS + EA_NATIONS + MA_NATIONS + LA_NATIONS

VICTORY_CONDITIONS = [
    [0, 'Standard', 'Nothing'], [2, 'Dominion', 'Dominion score req.'],
    [3, 'Provinces', 'Provinces required'], [4, 'Research', 'Research points req.'],
    [6, 'Thrones', 'Nbr of Ascension Points']
]

POPTYPES = [
    [25, 'Barbarians'], [26, 'Horse Tribe'], [27, 'Militia, Archers, Hvy Inf'],
    [28, 'Militia, Archers, Hvy Inf'], [29, 'Militia, Archers, Hvy Inf'],
    [30, 'Militia, Longbow, Knight'], [31, 'Tritons'], [32, 'Lt Inf, Hvy Inf, X-Bow'],
    [33, 'Lt Inf, Hvy Inf, X-Bow'], [34, 'Raptors'], [35, 'Slingers'], [36, 'Lizards'],
    [37, 'Woodsmen'], [38, 'Hoburg'], [39, 'Militia, Archers, Lt Inf'], [40, 'Amazon, Crystal'],
    [41, 'Amazon, Garnet'], ['42', 'Amazon, Jade'], ['43', 'Amazon, Onyx'], [44, 'Troglodytes'],
    [45, 'Tritons, Shark Knights'], [46, 'Amber Clan Tritons'], [47, 'X-Bow, Hvy Cavalry'],
    [48, 'Militia, Lt Inf, Hvy Inf'], [49, 'Militia, Lt Inf, Hvy Inf'],
    [50, 'Militia, Lt Inf, Hvy Inf'], [51, 'Militia, Lt Cav, Hvy Cav'],
    [52, 'Militia, Lt Cav, Hvy Cav'], [53, 'Militia, Lt Cav, Hvy Cav'], [54, 'Hvy Inf, Hvy Cavalry'],
    [55, 'Hvy Inf, Hvy Cavalry'], [56, 'Hvy Inf, Hvy Cavalry'], [57, 'Shamblers'],
    [58, 'Lt Inf, Hvy Inf, X-Bow'], [59, 'Militia, Lt Inf, Archers'], [60, 'Militia, Lt Inf, Archers'],
    [61, 'Vaettir, Trolls'], [62, 'Tribals, Deer'], [63, 'Tritons'], [64, 'Tritons'],
    [65, 'Ichtyids'], [66, 'Vaettir'], [67, 'Vaettir, Dwarven Smith'],
    [68, 'Slingers, Hvy Inf, Elephants'], [69, 'Asmeg'], [70, 'Vaettir, Svartalf'], [71, 'Trolls'],
    [72, 'Mermen'], [73, 'Tritons, Triton Knights'], [74, 'Lt Inf, Lt Cav, Cataphracts'],
    [75, 'Hoburg, LA'], [76, 'Hoburg, EA'], [77, 'Atavi Apes'], [78, 'Tribals, Wolf'],
    [79, 'Tribals, Bear'], [80, 'Tribals, Lion'], [81, 'Pale Ones'], [82, 'Tribals, Jaguar'],
    [83, 'Tribals, Toad'], [84, 'Cavemen'], [85, 'Kappa'], [86, 'Bakemono'], [87, 'Bakemono'],
    [88, 'Ko-Oni'], [89, 'Fir Bolg'], [90, 'Turtle Tribe Tritons'], [91, 'Shark Tribe Tritons'],
    [92, 'Shark Tribe, Shark Riders'], [93, 'Zotz'], [94, 'Lava-born'], [95, 'Ichtyid Shaman'],
    [96, 'Bone Tribe'], [97, 'Merrow'], [98, 'Kulullu'], [99, 'Bronze Hoplites'], [100, 'Bronze Hvy Inf'],
    [101, 'Bronze Hvy Cav, Hvy Inf'], [102, 'Bronze Hvy Spear'], [103, 'Cynocephalians'], [104, 'Bekrydes'],
    [105, 'Wet Ones'], [106, 'Nexus']
]

FORT = [
    [1, 'Palisades'], [2, 'Fortress'], [3, 'Castle'], [4, 'Citadel'], [5, 'Rock Walls'],
    [6, 'Fortress'], [7, 'Castle'], [8, 'Castle of Bronze and Crystal'], [9, 'Kelp Fort'],
    [10, 'Bramble Fort'], [11, 'City Palisades'], [12, 'Walled City'], [13, 'Fortified City'],
    [14, 'Great Walled City'], [15, 'Giant Palisades'], [16, 'Giant Fortress'], [17, 'Giant Castle'],
    [18, 'Giant Citadel'], [19, 'Grand Citadel'], [20, 'Ice Walls'], [21, 'Ice Fortress'],
    [22, 'Ice Castle'], [23, 'Ice Citadel'], [24, 'Wizards Tower'], [25, 'Citadel of Power'],
    [27, 'Fortified village'], [28, 'Wooden Fort'], [29, 'Crystal Citadel']
]

SPECIAL_NEIGHBOUR = [
    [0, 'Standard border'], [1, 'Mountain pass'], [2, 'River border'], [4, 'Impassable'], [8, 'Road']
]

# Region settings
########################################################################################################################

# Terrain preference vector is the weighting for each type of terrain
TERRAIN_PREF_BITS = [0, 16, 32, 64, 128, 256, 8388608]
TERRAIN_PREFERENCES = [         # TERRAIN_PREF_XXXX = [plains, highlands, swamp, waste, forest, farm, mountains]
    [5, 1, 1, 1, 2, 1, 1],      # Balanced
    [10, 1, 1, 1, 1, 1, 1],     # Plains
    [5, 1, 1, 1, 5, 1, 1],      # Forest
    [3, 3, 1, 1, 3, 1, 4],      # Mountains
    [3, 1, 0.5, 3, 1, 0.5, 1],  # Desert
    [3, 1, 3, 0.5, 2, 1, 1],    # Swamp
    [5, 1, 1, 1, 2, 1, 1]       # Karst
]
TERRAIN_PREF_BALANCED, TERRAIN_PREF_PLAINS, TERRAIN_PREF_FOREST, TERRAIN_PREF_MOUNTAINS, TERRAIN_PREF_DESERT, TERRAIN_PREF_SWAMP, TERRAIN_PREF_KARST = TERRAIN_PREFERENCES

# Layout preference vector informs the land-sea split
LAYOUT_PREFERENCES = [  # LAYOUT_PREF_XXXX = [cap circle split, rest of homeland split]
    [1.0, 0.95],        # Land
    [1.0, 0.85],        # Cave
    [0.8, 0.8],         # Coast
    [0.2, 0.8],         # Island
    [0, 0.6],           # Deeps
    [0.2, 0.6],         # Shallows
    [0, 0.5]            # Lakes
]
LAYOUT_PREF_LAND, LAYOUT_PREF_CAVE, LAYOUT_PREF_COAST, LAYOUT_PREF_ISLAND, LAYOUT_PREF_DEEPS, LAYOUT_PREF_SHALLOWS, LAYOUT_PREF_LAKES = LAYOUT_PREFERENCES

TERRAIN_2_HEIGHTS_DICT = {0: 0, 4: -600, 16: 200, 32: 50, 64: 300, 128: 90, 256: 250, 2048: -200, 4096: 1000, 8388608: 200, 68719476736: -1000}

# Homelands format: [Nation index, terrain preference, layout preference, capital terrain int, plane]
HOMELANDS_INFO = [
    # EA NATIONS
    [5, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],             # Arcoscephale
    [6, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],             # Mekone
    [7, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],             # Pangaea
    [8, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],             # Ermor
    [9, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],               # Sauromatia
    [10, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],           # Fomoria
    [11, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 128, 1],          # Tir na nog
    [12, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 128, 1],          # Marverni
    [13, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 128, 1],         # Ulm
    [14, TERRAIN_PREF_FOREST, LAYOUT_PREF_CAVE, 0, 2],              # Pyrene
    [15, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 0, 2],            # Agartha
    [16, TERRAIN_PREF_DESERT, LAYOUT_PREF_CAVE, 8388608, 2],        # Abysia
    [17, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Hinnom
    [18, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Ubar
    [19, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 0, 1],               # Ur
    [20, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 8388608, 1],        # Kailasa
    [21, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 8388608, 1],        # Lanka
    [22, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Tien Chi
    [23, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Yomi
    [24, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Caelum
    [25, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Mictlan
    [26, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 0, 2],            # Xibalba
    [27, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 32, 1],              # Ctis
    [28, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],              # Machaka
    [29, TERRAIN_PREF_DESERT, LAYOUT_PREF_COAST, 0, 1],             # Berytos
    [30, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],           # Vanheim
    [31, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Helheim
    [32, TERRAIN_PREF_KARST, LAYOUT_PREF_LAND, 0, 1],               # Rus
    [33, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Niefelheim
    [34, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Muspelheim
    [40, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 4, 1],          # Pelagia
    [41, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 132, 1],        # Oceania
    [42, TERRAIN_PREF_BALANCED, LAYOUT_PREF_SHALLOWS, 4, 1],        # Therodos
    [43, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS, 2052, 1],       # Atlantis
    [44, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS, 2052, 1],       # Ryleh

    # MA NATIONS
    [50, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Arcoscephale
    [51, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Phlegra
    [52, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Pangaea
    [53, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Asphodel
    [54, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Ermor
    [55, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Sceleria
    [56, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 0, 1],               # Pythium
    [57, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Man
    [58, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Eriu
    [59, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 0, 2],            # Agartha
    [60, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],           # Ulm
    [61, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Marignon
    [62, TERRAIN_PREF_KARST, LAYOUT_PREF_LAND, 128, 1],             # Pyrene
    [63, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 8388608, 2],      # Abysia
    [64, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Ashdod
    [65, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Naba
    [66, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Uruk
    [67, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Ind
    [68, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Bandar Log
    [69, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Tien Chi
    [70, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Shinuyama
    [71, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Caelum
    [72, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Nazca
    [73, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Mictlan
    [74, TERRAIN_PREF_SWAMP, LAYOUT_PREF_CAVE, 32, 2],              # Xibalba
    [75, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 32, 1],              # Ctis
    [76, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Machaka
    [77, TERRAIN_PREF_BALANCED, LAYOUT_PREF_ISLAND, 0, 1],          # Phaeacia
    [78, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],           # Vanheim
    [79, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Vanarus
    [80, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Jotunheim
    [81, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Nidavangr
    [85, TERRAIN_PREF_BALANCED, LAYOUT_PREF_SHALLOWS, 4, 1],        # Ys
    [86, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 4, 1],          # Pelagia
    [87, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 132, 1],        # Oceania
    [88, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 2052, 1],        # Atlantis
    [89, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 2052, 1],        # Ryleh

    # LA NATIONS
    [95, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Arcoscephale
    [96, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 8388608, 1],      # Phlegra
    [97, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Pangaea
    [98, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 0, 1],               # Pythium
    [99, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Lemuria
    [100, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],             # Man
    [101, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],          # Ulm
    [102, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 0, 2],           # Agartha
    [103, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Marignon
    [104, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 8388608, 2],     # Abysia
    [105, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],             # Ragha
    [106, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],    # Caelum
    [107, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],            # Gath
    [108, TERRAIN_PREF_KARST, LAYOUT_PREF_LAND, 128, 1],            # Patala
    [109, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],             # Tien Chi
    [110, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],          # Jomon
    [111, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],           # Mictlan
    [112, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 0, 2],           # Xibalba
    [113, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 32, 1],            # Ctis
    [115, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Midgard
    [116, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Bogarus
    [117, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Utgard
    [118, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],           # Vaettiheim
    [119, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Feminie
    [120, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Piconye
    [121, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],          # Andramania
    [122, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 128, 1],        # Pyrene
    [125, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Erytheia
    [126, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Atlantis
    [127, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 2052, 1],       # Ryleh

    # PLACEHOLDER NATIONS
    [300, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 0, 1],
    [400, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 0, 1],
    [500, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 0, 1]
]

# Periphery settings
PERIPHERY_INFO = [
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND],      # 0 BORDERS
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST],     # 1 COASTLINES
    [TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND],     # 2 MOUNTAINS
    [TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND],        # 3 WASTES
    [TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND],        # 4 DEEPWOODS
    [TERRAIN_PREF_KARST, LAYOUT_PREF_LAND],         # 5 OVERUNDER
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_ISLAND],    # 6 ARCHIPELAGO
    [TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAKES],        # 7 WETLANDS
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS],     # 8 SEABED
    [TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS],    # 9 ABYSS
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST],     # 10 DELTA
    [TERRAIN_PREF_KARST, LAYOUT_PREF_DEEPS]         # 11 UNDERSEA
]

# UNIVERSAL FUNCTIONS AND VARIABLES
########################################################################################################################

ROOT_DIR = Path(__file__).parent
REGION_TYPE = ['Throne', 'Homeland', 'Periphery']
PI_2 = 2 * np.pi
CAPITAL_POPULATION = 40000
AGE_POPULATION_MODIFIERS = [0.8, 1.0, 1.2]
AVERAGE_POPULATION_SIZES = [5500, 11000, 16500]
RESOURCE_SPECIFIC_TERRAINS = {4224: 1, 4112: 1.6, 4128: 2, 4096: 1, 132: 1, 20: 1.4, 2052: 1.2, 4: 1, 8388608: 2,
                              128: 1.6, 16: 1.4}

NEIGHBOURS_NO_WRAP = np.array([[0, 0]])
NEIGHBOURS_X_WRAP = np.array([[0, 0], [1, 0], [-1, 0]])
NEIGHBOURS_Y_WRAP = np.array([[0, 0], [0, 1], [0, -1]])
NEIGHBOURS_FULL = np.array([[0, 0], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [0, -1], [-1, -1], [-1, 0]])

DATASET_GRAPHS = [[[] for i in range(7)] for d in range(17)]
vertex = 0
graph_dict = {}
with open(ROOT_DIR / 'datasets/3_connected_graphs', 'r') as f:
    for line in f.readlines():
        data = line.split()
        if not data:
            DATASET_GRAPHS[vertex][degree].append(graph_dict)
            vertex = 0
            graph_dict = {}
            continue
        vertex += 1
        degree = len(data) - 1
        graph_dict[int(data[0].strip(':'))] = [int(x) for x in data[1:]]

PERIPHERY_DATA = []
with open(ROOT_DIR / 'datasets/peripheries', 'r') as f:
    for line in f.readlines():
        data = line.strip('\n')
        data = data.split('\t')
        PERIPHERY_DATA.append(list(map(int, data)))


def terrain_int2list(terrain_int):          # Function for separating terrain int into the components
    terrain_list = []
    binary = bin(terrain_int)[:1:-1]
    for x in range(len(binary)):
        if int(binary[x]):
            terrain_list.append(2**x)
    return terrain_list


def province_size_shape_calc(province, settings):  # Function for calculating the size of a province

    terrain_list = terrain_int2list(province.terrain_int)

    # do water and cave size setting
    if True:
        size = 1

    # do population sizing

    size = 1
    shape = 3

    # apply

    return size, shape


def terrain_2_resource_stats(terrain_int_list, age):

    resource_stats = []

    for terrain_int in terrain_int_list:

        average = 91
        if terrain_int & 1:
            average *= 0.5
        elif terrain_int & 2:
            average *= 1.5
        if terrain_int & 256:
            average *= 0.5

        for specific_terrain in RESOURCE_SPECIFIC_TERRAINS:
            if terrain_int & specific_terrain == specific_terrain:
                average *= RESOURCE_SPECIFIC_TERRAINS[specific_terrain]

        average *= AGE_POPULATION_MODIFIERS[age]
        resource_stats.append(average)

    return resource_stats


def nations_2_periphery(nations):
    t1 = TERRAIN_PREFERENCES.index(nations[0].terrain_profile)
    l1 = LAYOUT_PREFERENCES.index(nations[0].layout)
    t2 = TERRAIN_PREFERENCES.index(nations[1].terrain_profile)
    l2 = LAYOUT_PREFERENCES.index(nations[1].layout)
    return PERIPHERY_INFO[PERIPHERY_DATA[7*l1+t1][7*l2+t2]-1]


def dibber(class_object, seed):             # Setting the random seed, when no seed is provided the class seed is used
    if seed is None:
        seed = class_object.seed
    rd.seed(seed)


# Default settings
########################################################################################################################

DEFAULT_SETTINGS = 1

########################################################################################################################

# Importing classes and functions at the end avoids circular dependencies
from .numba_lloyd_relaxation import LloydRelaxation
from .numba_pixel_mapping import find_pixel_ownership, pb_pixel_allocation
from .functions_virtual_graph import make_virtual_graph
from .functions_find_edge_crossing import edge_crossing_detection
from .functions_graph_embedding import minor_graph_embedding
from .numba_spring_adjustment import spring_electron_adjustment
from .functions_map_plotting import plot_map_class, plot_torus_graph, plot_region
from .class_settings import DreamAtlasSettings
from .class_nation import Nation
from .class_province import Province
from .class_region import Region
from .class_map import DominionsMap
from .class_layout import DominionsLayout
from .generate_dreamatlas import DreamAtlas
