from DreamAtlas import *


def DreamAtlasGenerator(settings, seed=None):
    map_class = DominionsMap(1)
    map_class.settings = settings
    map_class.seed = settings.seed
    dibber(map_class, seed)

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
    map_class.map_size[1] = [4500, 2600]
    map_class.scale[1] = [450, 200]
    map_class.map_size[2] = [4500, 2600]
    map_class.scale[2] = [450, 200]
    map_class.planes = [1, 2]

    layout = DominionsLayout(map_class)
    layout.generate_region_layout()

    ########################################################################################################################
    # Assemble the regions and generate the initial province layout
    print('\nMaking regions....')
    fixed_points = {0}

    # Generate the homelands
    region_index = 1
    province_index = [1 for _ in range(10)]
    homeland_list = []
    allowed_nations_list = []
    special_start_locations = [[] for _ in range(10)]
    province_list = [[] for _ in range(10)]
    terrain_list = [[] for _ in range(10)]
    for nation in nation_list:
        new_homeland = Region(index=region_index, region_type='Homeland', nations=[nation], seed=settings.seed,
                              settings=settings)
        new_homeland.generate_graph()
        new_homeland.generate_terrain()
        new_homeland.generate_population()
        new_homeland.embed_region(global_coordinates=layout.region_coordinates[region_index],
                                  rotation=0,
                                  scale=map_class.scale[1],
                                  map_size=map_class.map_size[1])

        # Adding info to the map class
        for province in new_homeland.provinces:
            province.index = province_index[province.plane]
            province_list[province.plane].append(province)
            terrain_list[province.plane].append([province.index, province.terrain_int])
            province_index[province.plane] += 1

        homeland_list.append(new_homeland)
        allowed_nations_list.append(nation.index)
        special_start_locations[nation.home_plane].append([nation.index, new_homeland.provinces[0].index])
        fixed_points.add(new_homeland.provinces[0].index)
        region_index += 1

    # Generate the peripherals
    periphery_list = []
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
                                   rotation=layout.region_rotation[periphery_index],
                                   scale=map_class.scale[1],
                                   map_size=map_class.map_size[1])

        periphery_list.append(new_periphery)
        for province in new_periphery.provinces:
            province.index = province_index[province.plane]
            province_list[province.plane].append(province)
            terrain_list[province.plane].append([province.index, province.terrain_int])
            province_index[province.plane] += 1

        fixed_points.add(new_periphery.provinces[0].index)
        region_index += 1

    # # Generate the thrones
    throne_list = []
    for throne_index in range(region_index, region_index + 1 + map_class.settings.throne_count):
        new_throne = Region(index=region_index, region_type='Throne', nations=[], seed=map_class.seed,
                            settings=map_class.settings)
        new_throne.generate_graph()
        new_throne.generate_terrain()
        new_throne.generate_population()
        new_throne.embed_region(global_coordinates=layout.region_coordinates[throne_index],
                                rotation=0,
                                scale=map_class.scale[1],
                                map_size=map_class.map_size[1])

        throne_list.append(new_throne)
        for province in new_throne.provinces:
            province.index = province_index[province.plane]
            province_list[1].append(province)
            terrain_list[1].append([province.index, province.terrain_int])
            province_index[province.plane] += 1

        region_index += 1

    # Add the cave wall provinces
    cave_wall_dist = 300
    x_range = np.arange(1, map_class.map_size[2][0]-10, cave_wall_dist)
    y_range = np.arange(1, map_class.map_size[2][1]-10, 0.8660 * cave_wall_dist)
    for x in x_range:
        for y in y_range:
            new_wall = Province(province_index[2], plane=2, terrain_int=68719476736, population=0, capital_location=False, capital_nation=None, coordinates=[int(x), int(y)], size=0.8, shape=1)
            province_index[2] += 1
            new_wall.parent_region = -1
            province_list[2].append(new_wall)
            terrain_list[2].append([new_wall.index, new_wall.terrain_int])

    map_class.homeland_list = homeland_list
    map_class.allowed_nations_list = allowed_nations_list
    map_class.special_start_locations = special_start_locations
    map_class.periphery_list = periphery_list
    map_class.throne_list = throne_list
    map_class.province_list = province_list
    map_class.terrain_list = terrain_list

    print('\nMap assembly....')
    for plane in map_class.planes:
        layout.generate_province_layout(plane=plane)
        layout.generate_special_neighbours_gates(plane=plane)
        map_class.neighbour_list[plane], map_class.special_neighbour_list[plane], map_class.gate_list[plane], map_class.min_dist[plane] = layout.get_neighbour_lists(plane=plane)

    ########################################################################################################################
    # Do pixel mapping
    print('\nPixel Mapping....')
    for plane in map_class.planes:
        weights = {}
        shapes = {}
        for province in province_list[plane]:
            weights[province.index] = province.size
            shapes[province.index] = province.shape
        map_class.pixel_map[plane] = find_pixel_ownership(layout.coordinates[plane], map_class.map_size[plane], weights, shapes, hwrap=True, vwrap=True, scale_down=2)
        map_class.pixel_owner_list[plane] = pb_pixel_allocation(map_class.pixel_map[plane])

        height_dict = {0: -1}
        for province in map_class.province_list[plane]:
            height = 20
            if province.terrain_int & 4 == 4:
                height = -30
            if province.terrain_int & 2052 == 2052:
                height = -100
            height_dict[province.index] = height
        map_class.height_map[plane] = np.vectorize(lambda i: height_dict[i])(map_class.pixel_map[plane])

    map_class.layout = layout

    print('\nDreamAtlas generation complete!')

    return map_class
