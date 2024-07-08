import pathlib

from . import *


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
TERRAIN_2_SHAPES_DICT = {}

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
    [123, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 128, 1],        # Pyrene
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

ROOT_DIR = pathlib.Path(__file__).parent
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
with open(ROOT_DIR / 'three_connected_graphs', 'r') as f:
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
with open(ROOT_DIR / 'peripheries', 'r') as f:
    for line in f.readlines():
        data = line.strip('\n')
        data = data.split('\t')
        PERIPHERY_DATA.append(list(map(int, data)))
