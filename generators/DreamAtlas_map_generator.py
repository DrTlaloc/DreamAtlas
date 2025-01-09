from DreamAtlas import *
from DreamAtlas.classes.class_region import HomelandRegion, PeripheryRegion, ThroneRegion, CaveRegion, BlockerRegion


def generator_dreamatlas(settings: type(DreamAtlasSettings),
                         ui=None,
                         queue=None,
                         seed: int = None):
    def estimate_time(settings):
        return 45
    if ui is not None:
        ui.progress_bar.start(estimate_time(settings) * 10)

    def generator_logging(text):
        if ui is not None:
            ui.status_label_var.set(text)
        else:
            print(f'{text}')

    map_class = DominionsMap()
    map_class.settings, map_class.seed = settings, settings.seed
    dibber(map_class, seed)

    # Loading nations and making the nation -> graph dict
    generator_logging('Making nations...')
    nation_list, players_teams = list(), list()
    for nation_data in settings.nations:
        nation_list.append(Nation(nation_data))
    for custom_nation_data in settings.custom_nations:
        nation_list.append(CustomNation(custom_nation_data))

    # Generate the player layout graph, determine the map size/region scale
    generator_logging('Making region layout...')
    pixels = np.asarray([0, 2500000], dtype=np.uint32)
    for nation in nation_list:
        if nation.home_plane == 1:
            pixels[0] += 900000
        elif nation.home_plane == 2:
            pixels[0] += 450000
            pixels[1] += 450000

    map_class.map_size[1:3] = np.outer(np.sqrt(pixels), np.asarray([1, 0.588])).round(decimals=-2).astype(dtype=np.uint32)
    map_class.scale[1] = map_class.map_size[1] * np.asarray([0.04, 0.04])
    map_class.scale[2] = map_class.map_size[2] * np.asarray([0.02, 0.02])
    map_class.planes = [1, 2]

    cave_regions = int(0.05 * (len(nation_list) * settings.homeland_size + 0.5 * len(nation_list) * settings.player_neighbours * settings.periphery_size + settings.throne_sites))
    blockers = int(np.sqrt(2500000 - cave_regions * 2 * 45000) / 15)

    layout = DominionsLayout(map_class)
    layout.generate_region_layout(players_teams=settings.nations,
                                  player_connections=settings.player_neighbours,
                                  periphery_connections=2,
                                  throne_regions=settings.throne_sites,
                                  water_regions=0,
                                  cave_regions=cave_regions,
                                  vast_regions=0,
                                  blocker_regions=blockers,
                                  map_size=map_class.map_size[1],
                                  seed=map_class.seed)

    # Assemble the regions and generate the initial province layout
    generator_logging('Making regions....')
    
    homeland_list = list()
    periphery_list = list()
    throne_list = list()
    water_list = list()
    caves_list = list()
    vast_list = list()
    blocker_list = list()
    allowed_nations_list = list()
    special_start_locations = list()
    province_index = [1 for _ in range(10)]
    province_list = [[] for _ in range(10)]
    terrain_list = [[] for _ in range(10)]

    all_regions = list()

    for i in layout.region_graph:  # Generate all the regions

        if layout.region_types[i] == 0:  # Generate the homelands
            nation = nation_list[i - 1]
            new_region = HomelandRegion(index=i, nation=nation, settings=settings, seed=seed)
            homeland_list.append(new_region)
            allowed_nations_list.append(nation.index)

        elif layout.region_types[i] == 1:  # Generate the peripherals
            nations = [nation_list[layout.region_graph[i][0] - 1], nation_list[layout.region_graph[i][1] - 1]]
            new_region = PeripheryRegion(index=i, nations=nations, settings=settings, seed=map_class.seed)
            periphery_list.append(new_region)

        elif layout.region_types[i] == 2:  # Generate the thrones
            new_region = ThroneRegion(index=i, settings=map_class.settings, seed=map_class.seed)
            throne_list.append(new_region)

        elif layout.region_types[i] == 3:  # Generate the water regions
            x = 1

        elif layout.region_types[i] == 4:  # Generate the cave regions
            new_region = CaveRegion(index=i, settings=map_class.settings, seed=map_class.seed)
            caves_list.append(new_region)

        elif layout.region_types[i] == 5:  # Generate the vast regions
            x = 1

        elif layout.region_types[i] == 6:  # Generate the blocker regions
            new_region = BlockerRegion(index=i, blocker=0, settings=map_class.settings, seed=map_class.seed)
            blocker_list.append(new_region)

        all_regions.append(new_region)
        new_region.generate_graph()
        new_region.generate_terrain()
        new_region.generate_population()
        new_region.embed_region(global_coordinates=layout.region_coordinates[i], scale=map_class.scale, map_size=map_class.map_size)

        for province in new_region.provinces:
            province.index = province_index[province.plane]
            province_list[province.plane].append(province)
            province_index[province.plane] += 1

    for region in homeland_list:  # Curse you Illwinterrr!!!!!!
        for province in region.provinces:
            if province.capital_location:
                special_start_index = province.index
        if region.provinces[0].plane == 2:
            special_start_index += len(province_list[1])
        special_start_locations.append([region.nation.index, int(special_start_index)])

    map_class.homeland_list = homeland_list
    map_class.periphery_list = periphery_list
    map_class.throne_list = throne_list
    # water_list = list()
    # caves_list = list()
    # vast_list = list()
    # blocker_list = list()
    map_class.province_list = province_list

    generator_logging('Map assembly....')

    for plane in map_class.planes:
        layout.generate_province_layout(plane=plane)
        layout.generate_neighbours(plane=plane)
        layout.generate_special_neighbours(plane=plane)
    layout.generate_gates(all_regions=all_regions)

    # Check to add omni here
    if settings.omniscience:
        for province in province_list[2]:
            fail = False
            if not has_terrain(province.terrain_int, 68719476736):
                continue
            else:
                for i in layout.graph[2][province.index]:
                    i_province = province_list[2][i - 1]
                    if not has_terrain(i_province.terrain_int, 68719476736):
                        fail = True
            if not fail:
                break

        allowed_nations_list.append(499)
        special_start_locations.append([499, len(province_list[1]) + province.index])
        province.has_commands = True
        province.terrain_int = 4096
        province.population = 10000
        province.size = 2
        province.shape = 3

    for plane in map_class.planes:
        for province in province_list[plane]:  # Do this here in case of terrain changes from mountains (curse you Illwinter!!!!)
            terrain_list[plane].append([province.index, province.terrain_int])
            province.coordinates = layout.coordinates[plane][province.index]

    map_class.allowed_nations_list = allowed_nations_list
    map_class.special_start_locations = special_start_locations
    map_class.terrain_list = terrain_list
    map_class.neighbour_list = layout.neighbours
    map_class.min_dist = layout.min_dist
    map_class.special_neighbour_list = layout.special_neighbours
    map_class.gate_list = layout.gates

    ########################################################################################################################
    # Do pixel mapping
    generator_logging('Pixel mapping...')
    for plane in map_class.planes:
        shapes = dict()
        for province in province_list[plane]:
            shapes[province.index] = province.shape

        map_class.pixel_map[plane] = find_pixel_ownership(layout.coordinates[plane], map_class.map_size[plane], shapes,hwrap=True, vwrap=True, scale_down=8)
        map_class.pixel_owner_list[plane] = pb_pixel_allocation(map_class.pixel_map[plane])

        height_dict = dict()
        for province in map_class.province_list[plane]:
            height = 20
            if has_terrain(province.terrain_int, 4):
                height = -30
            if has_terrain(province.terrain_int, 2052):
                height = -100
            if has_terrain(province.terrain_int, 68719476736):  # testing cave wall rendering hypothesis
                height = -100
            height_dict[province.index] = height
        map_class.height_map[plane] = np.vectorize(lambda i: height_dict[i])(map_class.pixel_map[plane])

    map_class.layout = layout

    generator_logging('DreamAtlas generation complete!')
    if ui is not None:
        ui.progress_bar.stop()
    return map_class
