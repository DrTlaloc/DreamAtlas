# Imports all the DreamAtlas functionality and dependencies
from . import *


class DominionsMap:

    def __init__(self, index: int):  # Map classes always initialise empty to be filled in later

        # DreamAtlas required data
        self.index = index
        self.settings = None
        self.homeland_list = []
        self.periphery_list = []
        self.throne_list = []
        self.province_list = [[] for _ in range(10)]
        self.armies_list = [[] for _ in range(10)]
        self.pretenders_list = [[] for _ in range(10)]

        # Required map data/commands
        self.map_title = 'DreamAtlas_map_%i' % self.index
        self.image_file = [None for _ in range(10)]
        self.map_size = [[0, 0] for _ in range(10)]
        self.scale = [[0, 0] for _ in range(10)]
        self.planes = []

        # Basic map data/commands
        self.dom_version = '600'
        self.winter_image_file = [None]*9
        self.scenario = False
        self.description = "An exciting map made using Tlaloc\'s DreamAtlas!"
        self.neighbour_list = [[] for _ in range(10)]
        self.special_neighbour_list = [[] for _ in range(10)]
        self.pixel_owner_list = [[] for _ in range(10)]
        self.province_names_list = [[] for _ in range(10)]
        self.terrain_list = [[] for _ in range(10)]
        self.gate_list = [[] for _ in range(10)]

        # Advanced map data/commands
        self.map_text_colour = [1.0, 1.0, 1.0, 0]
        self.map_dom_colour = [255, 202, 255, 5]
        self.max_sail_distance = [2 for _ in range(10)]
        self.magic_sites = [60 for _ in range(10)]
        self.capital_names = True
        self.allowed_nations_list = []
        self.computer_player_list = []
        self.ai_allies_list = []
        self.victory_type = [6, 12]
        self.cannot_win_list = []
        self.victory_point_provinces = [[] for _ in range(10)]

        # Start location data/commands
        self.start_locations = [[] for _ in range(10)]
        self.no_start_locations = [[] for _ in range(10)]
        self.special_start_locations = [[] for _ in range(10)]
        self.team_start_locations = [[] for _ in range(10)]

        # Meta data (for later)
        self.seed = 0
        self.layout = None
        self.pixel_map = [None for _ in range(10)]
        self.pixel_owner_list = [[] for _ in range(10)]
        self.height_map = [None for _ in range(10)]
        self.min_dist = [None for _ in range(10)]

    def read_map_file(self, filepath):  # Instructs the map class to load in an existing .map file.

        with open(filepath, 'r') as f:
            lines = f.readlines()

            for line in lines:
                if line[0] != '#':
                    continue

                line = line.split()

                if line[0] == '#dom2title':
                    self.map_title = line[1]
                if line[0] == '#imagefile':
                    self.image_file = line[1]
                if line[0] == '#mapsize':
                    self.map_size = [int(line[1]), int(line[2])]

                if line[0] == '#domversion':
                    self.dom_version = int(line[1])
                if line[0] == '#winterimagefile':
                    self.winter_image_file = line[1]
                if line[0] == '#scenario':
                    self.scenario = True
                if line[0] == '#description':
                    self.description = ' '.join(line[1:])
                if line[0] == '#neighbour':
                    self.neighbour_list.append([int(line[1]), int(line[2])])
                if line[0] == '#neighbourspec':
                    self.special_neighbour_list.append([int(line[1]), int(line[2]), int(line[3])])
                if line[0] == '#pb':
                    self.pixel_owner_list.append([int(line[1]), int(line[2]), int(line[3]), int(line[4])])
                if line[0] == '#landname':
                    self.province_names_list.append([int(line[1]), ' '.join(line[2:])])

                if line[0] == '#terrain':
                    self.terrain_list.append([int(line[1]), int(line[2])])

                if line[0] == '#maptextcol':
                    self.map_text_colour = [float(line[1]), float(line[2]), float(line[3]), float(line[4])]
                if line[0] == '#mapdomcol':
                    self.map_dom_colour = [int(line[1]), int(line[2]), int(line[3]), int(line[4])]
                if line[0] == '#saildist':
                    self.max_sail_distance = int(line[1])
                if line[0] == '#features':
                    self.magic_sites = int(line[1])
                if line[0] == '#nohomelandnames':
                    self.capital_names = True
                # if line[0] == '#nonamefilter':
                #     self.no_names = True
                if line[0] == '#allowedplayer':
                    self.allowed_nations_list.append(int(line[1]))
                if line[0] == '#computerplayer':
                    self.computer_player_list.append([int(line[1]), int(line[2])])
                if line[0] == '#allies':
                    self.ai_allies_list.append([int(line[1]), int(line[2])])
                if line[0] == '#victorycondition':
                    self.victory_type = [int(line[1]), int(line[2])]
                if line[0] == '#cannotwin':
                    self.cannot_win_list.append(int(line[1]))
                if line[0] == '#victorypoints ':
                    self.victory_point_provinces.append([int(line[1]), int(line[2])])

                if line[0] == '#start':
                    self.start_locations.append(int(line[1]))
                if line[0] == '#nostart':
                    self.no_start_locations.append(int(line[1]))
                if line[0] == '#specstart':
                    self.special_start_locations.append([int(line[1]), int(line[2])])
                if line[0] == '#teamstart':
                    self.special_start_locations.append([int(line[1]), int(line[2])])

    def make_map_file(self,
                      plane: int,
                      filepath: str = None):  # Instructs the map class to print a .map file with a specific name (should really be the map name)

        if filepath is None:
            filepath = '%s.map' % self.map_title[plane]

        with open(filepath, 'w') as f:

            f.write('--This map file was made using DreamAtlas\n\n')
            f.write('--General Map Information\n')
            f.write('#dom2title %s\n' % self.map_title[plane])
            f.write('#imagefile %s\n' % self.image_file[plane])
            # f.write('#winterimagefile %s\n' % self.winter_image_file[plane])
            f.write('#mapsize %s %s\n' % (self.map_size[plane][0], self.map_size[plane][1]))
            f.write('#wraparound\n')
            if not self.capital_names:
                f.write('#nohomelandnames\n')
            if self.scenario:
                f.write('#scenario\n')
            if self.dom_version is not None:
                f.write('#domversion %s\n' % self.dom_version)
            f.write('#maptextcol ' + ' '.join(map(str, self.map_text_colour)) + '\n')
            f.write('#mapdomcol ' + ' '.join(map(str, self.map_dom_colour)) + '\n')
            if plane == 2:
                f.write('#planename The Realm Beneath\n')
            if self.victory_type is not None:
                f.write('#victorycondition %s %s\n' % (self.victory_type[0], self.victory_type[1]))

            f.write('#nodeepcaves\n')
            f.write('#nodeepchoice\n')
            if self.max_sail_distance[plane] is not None:
                f.write('#saildist %s\n' % self.max_sail_distance[plane])
            if self.magic_sites[plane] is not None:
                f.write('#features %s\n' % self.magic_sites[plane])
            f.write('#description %s\n' % self.description)

            # Nation info
            f.write('\n--Nation info\n')
            if len(self.allowed_nations_list) != 0:
                for entry in range(len(self.allowed_nations_list)):
                    f.write('#allowedplayer %s\n' % self.allowed_nations_list[entry])
            if len(self.computer_player_list) != 0:
                for entry in range(len(self.computer_player_list)):
                    f.write('#computerplayer ' + ' '.join(map(str, self.computer_player_list[entry])) + '\n')
            if len(self.ai_allies_list) != 0:
                for entry in range(len(self.ai_allies_list)):
                    f.write('#allies ' + ' '.join(map(str, self.ai_allies_list[entry])) + '\n')
            if len(self.cannot_win_list) != 0:
                for entry in range(len(self.cannot_win_list)):
                    f.write('#cannotwin %s\n' % self.cannot_win_list[entry])

            f.write('\n--Province start info\n')
            if len(self.start_locations[plane]) != 0:
                for entry in range(len(self.start_locations[plane])):
                    f.write('#start %s\n' % self.start_locations[plane][entry])
            if len(self.no_start_locations[plane]) != 0:
                for entry in range(len(self.no_start_locations[plane])):
                    f.write('#nostart %s\n' % self.no_start_locations[plane][entry])
            if plane == 1:
                if len(self.special_start_locations[plane]) != 0:
                    for entry in range(len(self.special_start_locations)):
                        f.write('#specstart ' + ' '.join(map(str, self.special_start_locations[entry])) + '\n')
            if len(self.team_start_locations[plane]) != 0:
                for entry in range(len(self.team_start_locations[plane])):
                    f.write('#teamstart ' + ' '.join(map(str, self.team_start_locations[plane][entry])) + '\n')

            # Unique province info
            if len(self.victory_point_provinces[plane]) != 0:
                for entry in range(len(self.victory_point_provinces[plane])):
                    f.write('#victorypoints ' + ' '.join(map(str, self.victory_point_provinces[plane][entry])) + '\n')

            if len(self.province_names_list[plane]) != 0:
                f.write('\n--Unique province names\n')
                for entry in range(len(self.province_names_list[plane])):
                    f.write('#landname ' + ' '.join(map(str, self.province_names_list[plane][entry])) + '\n')

            # Terrain info
            if len(self.terrain_list[plane]) != 0:
                f.write('\n--Terrain info\n')
                for entry in range(len(self.terrain_list[plane])):
                    f.write('#terrain ' + ' '.join(map(str, self.terrain_list[plane][entry])) + '\n')

            # Neighbour info
            if len(self.neighbour_list[plane]) != 0:
                f.write('\n--Neighbour info\n')
                for entry in range(len(self.neighbour_list[plane])):
                    f.write('#neighbour ' + ' '.join(map(str, self.neighbour_list[plane][entry])) + '\n')
            if len(self.special_neighbour_list[plane]) != 0:
                f.write('\n--Special Neighbour info\n')
                for entry in range(len(self.special_neighbour_list[plane])):
                    f.write('#neighbourspec ' + ' '.join(map(str, self.special_neighbour_list[plane][entry])) + '\n')
            if len(self.gate_list[plane]) != 0:
                f.write('\n--Gate info\n')
                for entry in range(len(self.gate_list[plane])):
                    f.write('#gate ' + ' '.join(map(str, self.gate_list[plane][entry])) + '\n')

            # Province commands
            for province in self.province_list[plane]:
                if province.has_commands:
                    f.write('#setland %i\n' % province.index)
                    if province.population is not None:
                        f.write('#population %i\n' % province.population)

            # Pixel ownership info
            f.write('\n--Pixel ownership info\n')
            if len(self.pixel_owner_list[plane]) != 0:
                for entry in range(len(self.pixel_owner_list[plane])):
                    f.write('#pb ' + ' '.join(map(str, self.pixel_owner_list[plane][entry])) + '\n')

            f.write('\n--The End\n')
            f.write('--(P.S. if you\'re reading this then I hope you have a nice day)')

    def file_2_atlas(self):

        # Filling out various parts of the DreamAtlas map class based on existing data
        # (used after loading a .map file)

        # Make all the province classes
        done_provs = []
        coordinate_dict = {}
        for terrain in self.terrain_list:
            owner, terrain_int = terrain
            if owner not in done_provs:
                done_provs.append(owner)
                coordinate_dict[owner] = []
                self.province_list.append(Province(index=owner, terrain_int=terrain_int))

        # Make the pixel map
        self.pixel_map = np.zeros([self.map_size[0], self.map_size[1]])
        self.height_map = np.zeros([self.map_size[0], self.map_size[1]])
        for pb in self.pixel_owner_list:
            x, y, len, owner = pb
            for pixel in range(len):
                self.pixel_map[x + pixel][y] = owner
                coordinate_dict[owner].append([x + pixel, y])

                # Make the height map
                province = self.province_list[owner - 1]
                self.height_map[x + pixel][y] = 20
                if province.terrain_int & 4:
                    self.height_map[x + pixel][y] = -30
                if province.terrain_int & 2052 == 2052:
                    self.height_map[x + pixel][y] = -100

        # Work out the province centres and min dist
        for owner in done_provs:
            counter = 0
            x_sum = 0
            y_sum = 0
            for entry in coordinate_dict[owner]:
                counter += 1
                x_sum += entry[0]
                y_sum += entry[1]

            province = self.province_list[owner - 1]
            province.coordinates = [x_sum / counter, y_sum / counter]

    def make_d6m(self,
                 plane: int,
                 filepath: str = None):

        with open(filepath, "wb") as f:  # Format is little endian binary which requires data to be converted

            # Write headline map data
            f.write(struct.pack("<iiiiqhii", 898933, 3, int(self.map_size[plane][0]), int(self.map_size[plane][1]), 0,
                                int((self.min_dist[plane] % 1.0) * 10000), int(self.min_dist[plane]), int(len(self.province_list[plane]))))

            for province in self.province_list[plane]:  # Write pixel positions of each 'capital' (fort) and the 'spec' (if its deep sea, unknown why this is)
                x, y = province.coordinates
                f.write(struct.pack("<hhq", int(x), int(y), province.terrain_int & 2052))

            for height in np.ndarray.flatten(self.height_map[plane], order='F'):  # Write height for each pixel
                f.write(struct.pack("<h", int(height)))

            for owner in np.ndarray.flatten(self.pixel_map[plane], order='F'):  # Write ownership for each pixel
                f.write(struct.pack("<h", int(owner)))
            
            f.write(struct.pack("<i", 1155))  # Write final 'magic number' (allows dom6.exe to recognise the file)

    def publish(self,
                location: str = None,
                name: str = None):

        if location is None:
            location = r"C:\Users\amyau\PycharmProjects\mapTlaloc\test_maps"
        if name is None:
            name = 'DreamAtlas_%i' % self.index
        map_folder = os.path.join(location, name)
        os.mkdir(map_folder)

        for plane in self.planes:
            plane_str = '_plane%i' % plane
            if plane == 1:
                plane_str = ''

            if self.settings.art_style == 0:
                self.image_file[plane] = '%s%s.d6m' % (name, plane_str)  # Make surface
                self.make_map_file(plane=plane, filepath=os.path.join(map_folder, '%s%s.map' % (name, plane_str)))
                self.make_d6m(plane=plane, filepath=os.path.join(map_folder, '%s%s.d6m' % (name, plane_str)))
            else:
                return Exception("No valid artstyle")

    def plot(self):  # Making the figures (general map, regions, terrain, population)

        fig1, axs1 = plt.subplots(len(self.planes), 1)
        fig2, axs2 = plt.subplots(len(self.planes), 1)
        fig3, axs3 = plt.subplots(len(self.planes), 1)
        fig4, axs4 = plt.subplots(len(self.planes), 1)

        for index in range(len(self.planes)):
            plane = self.planes[index]
            map_x, map_y = self.map_size[plane]
            plane_axs = [axs1[index], axs2[index], axs3[index], axs4[index]]

            for ax in plane_axs:
                ax.set(xlim=[0, map_x], ylim=[0, map_y])

            index_dict, region_dict, terrain_dict, population_dict = {0: 0}, {0: -1}, {0: -1}, {0: -1}
            for province in self.province_list[plane]:
                index_dict[province.index] = province.index
                region_dict[province.index] = province.parent_region
                terrain_dict[province.index] = 0
                for terrain in terrain_int2list(province.terrain_int):
                    if terrain in TERRAIN_2_HEIGHTS_DICT:
                        terrain_dict[province.index] += TERRAIN_2_HEIGHTS_DICT[terrain]
                population_dict[province.index] = province.population

            plotting_pixel_map = np.transpose(self.pixel_map[plane])
            plane_general = np.vectorize(lambda i: index_dict[i])(plotting_pixel_map)
            plane_regions = np.vectorize(lambda i: region_dict[i])(plotting_pixel_map)
            plane_terrain = np.vectorize(lambda i: terrain_dict[i])(plotting_pixel_map)
            plane_population = np.vectorize(lambda i: population_dict[i])(plotting_pixel_map)

            # Plotting the contourf and the province border contour map
            plane_axs[0].imshow(plane_general, cmap=cm.Pastel1)
            plane_axs[0].contour(plane_general, levels=max(self.layout.graph[plane]), colors=['white', ])
            plane_axs[1].imshow(plane_regions, vmin=1, vmax=len(self.layout.region_graph), cmap=cm.tab20)
            plane_axs[1].contour(plane_regions, levels=max(self.layout.graph[plane]), colors=['white', ])
            plane_axs[2].imshow(plane_terrain, vmin=-200, vmax=600, cmap=cm.terrain)
            plane_axs[2].contour(plane_terrain, levels=max(self.layout.graph[plane]), colors=['white', ])
            plane_axs[3].imshow(plane_population, cmap=cm.YlGn)
            plane_axs[3].contour(plane_general, levels=max(self.layout.graph[plane]), colors=['white', ])

            virtual_graph, virtual_coordinates = make_virtual_graph(self.layout.graph[plane], self.layout.coordinates[plane],
                                                                    self.layout.darts[plane], self.map_size[plane])
            for i in virtual_graph:
                x0, y0 = virtual_coordinates[i]
                for j in virtual_graph[i]:
                    x1, y1 = virtual_coordinates[j]
                    for ax in plane_axs:
                        ax.plot([x0, x1], [y0, y1], 'k-')

            for province in self.province_list[plane]:
                x0, y0 = province.coordinates
                if province.capital_location:
                    colour = 'bo'
                elif province.fixed:
                    colour = 'yo'
                else:
                    colour = 'ro'
                for ax in plane_axs:
                    ax.plot(x0, y0, colour)
                    ax.text(x0, y0, str(province.index))

    # Printing the class returns this
    def __str__(self):
        return '%s : %s' % (self.map_title, self.description)
