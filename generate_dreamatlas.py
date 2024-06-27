from . import *


def DreamAtlas(settings, seed=None):
    map_class = DominionsMap(1, settings=settings)
    dibber(map_class, seed)

    # Resetting map data
    map_class.province_list = []

    ########################################################################################################################
    # Loading nations and making the nation -> graph dict
    print('Loading nations....')
    nation_list = []
    for nation_index in settings.nations:
        nation_list.append(Nation(nation_index))
    rd.shuffle(nation_list)

    ########################################################################################################################
    # Generate the player layout graph, determine the map size/region scale
    print('\nMaking player layout....')
    map_class.map_size = [2000, 1000]
    map_class.scale = [150, 90]

    layout = DominionsLayout(map_class)
    layout.generate_region_layout()

    ########################################################################################################################
    # Assemble the regions and generate the initial province layout
    print('\nMaking regions....')
    fixed_points = {0}

    # Generate the homelands
    region_index = 1
    province_index = 1
    for nation in nation_list:
        new_homeland = Region(index=region_index, region_type='Homeland', nations=[nation], seed=settings.seed,
                              settings=settings)
        new_homeland.generate_graph()
        new_homeland.generate_terrain()
        new_homeland.generate_population()
        new_homeland.embed_region(global_coordinates=layout.region_coordinates[region_index],
                                  initial_index=province_index,
                                  rotation=0,
                                  scale=map_class.scale,
                                  map_size=map_class.map_size)

        map_class.homeland_list.append(new_homeland)  # Adding to the map class
        for province in new_homeland.provinces:
            map_class.province_list.append(province)

        fixed_points.add(province_index)
        region_index += 1
        province_index += len(new_homeland.provinces)

    # Generate the peripherals
    for periphery_index in range(region_index, 1 + int(0.5 * len(settings.nations) * settings.player_neighbours)):
        connected_homelands = layout.region_graph[periphery_index]
        nations = [nation_list[connected_homelands[0] - 1], nation_list[connected_homelands[1] - 1]]

        # Make the region class
        new_periphery = Region(index=region_index, region_type='Periphery', nations=nations, seed=settings.seed,
                               settings=settings)
        new_periphery.generate_graph()
        new_periphery.generate_terrain()
        new_periphery.generate_population()
        new_periphery.embed_region(global_coordinates=layout.region_coordinates[periphery_index],
                                   initial_index=province_index,
                                   rotation=layout.region_rotation[periphery_index],
                                   scale=map_class.scale,
                                   map_size=map_class.map_size)

        map_class.periphery_list.append(new_periphery)
        for province in new_periphery.provinces:
            map_class.province_list.append(province)

        fixed_points.add(province_index)
        region_index += 1
        province_index += len(new_periphery.provinces)

    # # Generate the thrones
    for throne_index in range(region_index, region_index + 1 + map_class.settings.throne_count):
        new_throne = Region(index=region_index, region_type='Throne', nations=[], seed=map_class.seed,
                            settings=map_class.settings)
        new_throne.generate_graph()
        new_throne.generate_terrain()
        new_throne.generate_population()
        new_throne.embed_region(global_coordinates=layout.region_coordinates[throne_index],
                                initial_index=province_index,
                                rotation=0,
                                scale=(1, 1),
                                map_size=map_class.map_size)

        map_class.province_list.append(new_throne.provinces[0])
        region_index += 1
        province_index += 1

    # Add the cave wall provinces
    cave_wall_list = []
    cave_wall_dist = 100
    x_range = np.arange(1, map_class.map_size[0]-10, cave_wall_dist)
    y_range = np.arange(1, map_class.map_size[1]-10, 0.8660 * cave_wall_dist)
    for x in x_range:
        for y in y_range:
            province_index += 1
            new_wall = Province(province_index, plane=2, terrain_int=68719476736, population=0, capital_location=False, capital_nation=None, coordinates=[int(x), int(y)], size=0.5, shape=1)
            new_wall.parent_region = -1
            cave_wall_list.append(new_wall)
    map_class.province_list.extend(cave_wall_list)

    print('\nMap assembly....')
    layout.generate_province_layout()
    # layout.generate_neighbours_gates()

    for province in map_class.province_list:
        if province.plane == 1:
            province.coordinates = layout.surface_coordinates[province.index]
        if province.plane == 2:
            province.coordinates = layout.ug_coordinates[province.index]

    ########################################################################################################################
    # Check the initial province layout and readjust if necessary

    ########################################################################################################################
    # Do pixel mapping
    print('\nPixel Mapping....')
    map_class.surface_pixel_map = find_pixel_ownership(layout.surface_coordinates, map_class.map_size, hwrap=True,
                                                       vwrap=True, scale_down=4)

    map_class.ug_pixel_map = find_pixel_ownership(layout.ug_coordinates, map_class.map_size, hwrap=True,
                                                  vwrap=True, scale_down=4)

    map_class.surface_pixel_owner_list = pb_pixel_allocation(map_class.surface_pixel_map)
    map_class.ug_pixel_owner_list = pb_pixel_allocation(map_class.ug_pixel_map)
    map_class.layout = layout

    print('\nDreamAtlas generation complete!')

    return map_class
