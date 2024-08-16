from DreamAtlas import *


def DreamAtlasGenerator(settings, seed=None):
    map_class = DominionsMap(settings.index)
    map_class.settings = settings
    map_class.seed = settings.seed
    dibber(map_class, seed)

    ########################################################################################################################
    # Loading nations and making the nation -> graph dict
    print('Loading nations....')
    nation_list = list()
    for nation_index in settings.nations:
        nation_list.append(Nation(nation_index))
    for custom_nation_data in settings.custom_nations:
        nation_list.append(CustomNation(custom_nation_data))
    rd.shuffle(nation_list)

    ########################################################################################################################
    # Generate the player layout graph, determine the map size/region scale
    print('\nMaking player layout....')
    pixels, ug_nations = [0, 4000000], 0
    for nation in nation_list:
        if nation.home_plane == 1:
            pixels[0] += 900000
        elif nation.home_plane == 2:
            pixels[0] += 450000
            pixels[1] += 450000
            ug_nations += 1
    l1, l2 = np.sqrt(pixels[0] / 1.7), np.sqrt(pixels[1] / 1.7)
    map_class.map_size[1], map_class.map_size[2] = [int(round(1.7*l1, -2)), int(round(l1, -2))],  [int(round(1.7*l2, -2)), int(round(l2, -2))]
    map_class.scale[1], map_class.scale[2] = [0.05*map_class.map_size[1][0], 0.05*map_class.map_size[1][1]], [0.02*map_class.map_size[2][0], 0.02*map_class.map_size[2][1]]
    map_class.planes = [1, 2]

    layout = DominionsLayout(map_class)
    layout.generate_region_layout(seed=seed)

    ########################################################################################################################
    # Assemble the regions and generate the initial province layout
    print('\nMaking regions....')
    # Generate the homelands
    province_index = [1 for _ in range(10)]
    homeland_list = []
    allowed_nations_list = []
    special_start_locations = []
    province_list = [[] for _ in range(10)]
    terrain_list = [[] for _ in range(10)]
    region_index = 1
    for nation in nation_list:
        new_homeland = Region(index=region_index, region_type='Homeland', nations=[nation], seed=settings.seed, settings=settings)
        new_homeland.generate_graph()
        new_homeland.generate_terrain()
        new_homeland.generate_population()
        new_homeland.embed_region(global_coordinates=layout.region_coordinates[region_index], rotation=0, scale=map_class.scale, map_size=map_class.map_size)

        # Adding info to the map class
        new_homeland.provinces[0].fixed = True
        for province in new_homeland.provinces:
            province.index = province_index[province.plane]
            province_list[province.plane].append(province)
            province_index[province.plane] += 1

        homeland_list.append(new_homeland)
        allowed_nations_list.append(nation.index)
        region_index += 1

    # Generate the peripherals
    periphery_list = []
    for periphery_index in range(region_index, region_index + int(0.5 * len(nation_list) * settings.player_neighbours)):
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
                                   scale=map_class.scale,
                                   map_size=map_class.map_size)

        periphery_list.append(new_periphery)
        for province in new_periphery.provinces:
            province.index = province_index[province.plane]
            province_list[province.plane].append(province)
            province_index[province.plane] += 1
        region_index += 1

    # # Generate the thrones
    throne_list = []
    for throne_index in range(region_index, region_index + map_class.settings.throne_sites):
        new_throne = Region(index=region_index, region_type='Throne', nations=[], seed=map_class.seed,
                            settings=map_class.settings)
        new_throne.generate_graph()
        new_throne.generate_terrain()
        new_throne.generate_population()
        new_throne.embed_region(global_coordinates=layout.region_coordinates[throne_index], rotation=0, scale=map_class.scale, map_size=map_class.map_size)

        throne_list.append(new_throne)
        new_throne.provinces[0].fixed = True
        for province in new_throne.provinces:
            province.index = province_index[province.plane]
            province_list[1].append(province)
            province_index[province.plane] += 1
        region_index += 1

    # Add the cave wall provinces and seed random minor caves
    cave_wall_dist = int(min(map_class.map_size[2]) / 10)
    x_range = np.arange(1, map_class.map_size[2][0]-10, cave_wall_dist)
    y_range = np.arange(1, map_class.map_size[2][1]-10, 0.8660 * cave_wall_dist)
    cave_walls = list()
    for x in x_range:
        for y in y_range:
            new_wall = Province(province_index[2], plane=2, terrain_int=4096+68719476736+576460752303423488, population=0, capital_location=False, capital_nation=None, coordinates=[int(x), int(y)], size=2, shape=1)
            province_index[2] += 1
            new_wall.parent_region = -1
            province_list[2].append(new_wall)
            cave_walls.append(new_wall)

    for region in homeland_list:  # Curse you Illwinterrr!!!!!!
        nation = region.nations[0]
        special_start_index = region.provinces[0].index
        if region.provinces[0].plane == 2:
            special_start_index += len(province_list[1])
        special_start_locations.append([nation.index, int(special_start_index)])

    map_class.homeland_list = homeland_list
    map_class.allowed_nations_list = allowed_nations_list
    map_class.special_start_locations = special_start_locations
    map_class.periphery_list = periphery_list
    map_class.throne_list = throne_list
    map_class.province_list = province_list

    print('\nMap assembly....')
    for plane in map_class.planes:
        layout.generate_province_layout(plane=plane)
        layout.generate_neighbours(plane=plane)
        layout.generate_special_neighbours(plane=plane)
    layout.generate_gates()

    minor_caves = int(0.1 * len(province_list[1]))
    cave_peripheries = rd.sample(periphery_list, minor_caves)
    pair_peripheries = [cave_peripheries[i:i+2] for i in range(0, len(cave_peripheries), 2)]
    gate = layout.gates[1][-1][1]
    for pair in pair_peripheries:
        surface_provinces, new_cave = list(), list()
        for periphery in pair:
            for province in periphery.provinces:
                if not has_terrain(province.terrain_int, 4):
                    surface_provinces.append(province)
                    break

        # select two adjacent walls to change
        rd.shuffle(cave_walls)
        for wall in cave_walls:
            fail = False
            if not has_terrain(wall.terrain_int, 68719476736):
                fail = True
            else:
                for i in layout.graph[2][wall.index]:
                    i_province = province_list[2][i-1]
                    if not has_terrain(i_province.terrain_int, 68719476736):
                        fail = True
                        break
                    else:
                        for j in layout.graph[2][i_province.index]:
                            j_province = province_list[2][j-1]
                            if not has_terrain(j_province.terrain_int, 68719476736):
                                fail = True
                                break
            if not fail:
                new_cave = [wall, i_province]
                break

        # update wall province info
        for province in new_cave:
            province.has_commands = True
            province.terrain_int = 4096
            province.parent_region = region_index
            province.population = 9000
            province.size = settings.cave_province_size
            province.shape = 3

        gate += 2
        layout.gates[1].append([surface_provinces[0].index, gate-1])
        layout.gates[2].append([wall.index, gate-1])
        layout.gates[1].append([surface_provinces[1].index, gate])
        layout.gates[2].append([i_province.index, gate])

    for plane in map_class.planes:
        for province in province_list[plane]:  # Do this here in case of terrain changes from mountains (curse Illwinter)
            terrain_list[plane].append([province.index, province.terrain_int])
            province.coordinates = layout.coordinates[plane][province.index]

    map_class.terrain_list = terrain_list
    map_class.neighbour_list = layout.neighbours
    map_class.min_dist = layout.min_dist
    map_class.special_neighbour_list = layout.special_neighbours
    map_class.gate_list = layout.gates

    ########################################################################################################################
    # Do pixel mapping
    print('\nPixel Mapping....')
    for plane in map_class.planes:
        weights = {}
        shapes = {}
        for province in province_list[plane]:
            weights[province.index] = province.size
            shapes[province.index] = province.shape
        map_class.pixel_map[plane] = find_pixel_ownership(layout.coordinates[plane], map_class.map_size[plane], weights, shapes, hwrap=True, vwrap=True, scale_down=8)
        map_class.pixel_owner_list[plane] = pb_pixel_allocation(map_class.pixel_map[plane])

        height_dict = {0: -1}
        for province in map_class.province_list[plane]:
            height = 20
            if province.terrain_int & 4 == 4:
                height = -30
            if province.terrain_int & 2052 == 2052:
                height = -100
            if province.terrain_int & 68719476736 == 68719476736:  # testing cave wall rendering hypothesis
                height = -100
            height_dict[province.index] = height
        map_class.height_map[plane] = np.vectorize(lambda i: height_dict[i])(map_class.pixel_map[plane])

    map_class.layout = layout

    print('\nDreamAtlas generation complete! \n\n')

    return map_class
