import numpy as np

from . import *


def terrain_int2list(terrain_int):          # Function for separating terrain int into the components
    terrain_list = []
    binary = bin(terrain_int)[:1:-1]
    for x in range(len(binary)):
        if int(binary[x]):
            terrain_list.append(2**x)
    return terrain_list


def find_shape_size(province, settings):  # Function for calculating the size of a province

    terrain_int = province.terrain_int
    terrain_list = terrain_int2list(terrain_int)
    size = 1
    shape = 2

    # size - terrain
    if terrain_int & 4:  # sea
        size *= settings.water_province_size
    if terrain_int & 4096:  # cave
        size *= settings.cave_province_size
    size *= 2 / (1 + np.e ** (0.01 * (province.population / 10000 - 1)))  # size - population

    # shape
    for terrain in TERRAIN_2_SHAPES_DICT:
        if terrain in terrain_list:
            shape *= TERRAIN_2_SHAPES_DICT[terrain]

    return size, shape


def terrain_2_resource_stats(terrain_int_list: list[int, ...],
                             age: int):

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


def dibber(class_object, seed):  # Setting the random seed, when no seed is provided the class seed is used
    if seed is None:
        seed = class_object.seed
    rd.seed(seed)


