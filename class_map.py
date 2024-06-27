# Imports all the DreamAtlas functionality and dependencies
from . import *


class DominionsMap:

    def __init__(self, index, settings=None, province_list=None, armies_list=None, pretenders_list=None, map_title=None,
                 image_file=None, map_size=None, dom_version=None, winter_image_file=None, scenario=False,
                 description=None, neighbour_list=None, special_neighbour_list=None, pixel_owner_list=None,
                 province_names_list=None, terrain_list=None, map_text_colour=None, map_dom_colour=None,
                 max_sail_distance=None, magic_sites=None, capital_names=True, allowed_nations_list=None,
                 computer_player_list=None, ai_allies_list=None, victory_type=None, cannot_win_list=None,
                 victory_point_provinces=None, start_locations=None, no_start_locations=None,
                 special_start_locations=None, team_start_locations=None, homeland_list=None, periphery_list=None,
                 throne_list=None):

        # DreamAtlas required data
        self.index = index
        if settings is None:
            settings = DEFAULT_SETTINGS
        self.settings = settings
        if homeland_list is None:
            homeland_list = []
        self.homeland_list = homeland_list
        if periphery_list is None:
            periphery_list = []
        self.periphery_list = periphery_list
        if throne_list is None:
            throne_list = []
        self.throne_list = throne_list
        if province_list is None:
            province_list = []
        self.province_list = province_list
        if armies_list is None:
            armies_list = []
        self.armies_list = armies_list
        if pretenders_list is None:
            pretenders_list = []
        self.pretenders_list = pretenders_list

        # Required map data/commands
        if map_title is None:
            map_title = 'Example_DreamAtlas_%i' % self.index
        self.map_title = map_title
        self.image_file = image_file
        if map_size is None:
            map_size = [0, 0]
        self.map_size = map_size
        self.scale = 75

        # Basic map data/commands
        self.dom_version = dom_version
        self.winter_image_file = winter_image_file
        self.scenario = scenario
        if description is None:
            description = "An exciting map made using Tlaloc\'s DreamAtlas!"
        self.description = description
        if neighbour_list is None:
            neighbour_list = []
        self.neighbour_list = neighbour_list
        if special_neighbour_list is None:
            special_neighbour_list = []
        self.special_neighbour_list = special_neighbour_list
        if pixel_owner_list is None:
            pixel_owner_list = []
        self.pixel_owner_list = pixel_owner_list
        if province_names_list is None:
            province_names_list = []
        self.province_names_list = province_names_list

        # Terrain data
        if terrain_list is None:
            terrain_list = []
        self.terrain_list = terrain_list

        # Advanced map data/commands
        if map_text_colour is None:
            map_text_colour = [1.0, 1.0, 1.0, 0]
        self.map_text_colour = map_text_colour
        if map_dom_colour is None:
            map_dom_colour = [255, 255, 29, 37]
        self.map_dom_colour = map_dom_colour
        self.max_sail_distance = max_sail_distance
        self.magic_sites = magic_sites
        self.capital_names = capital_names
        if allowed_nations_list is None:
            allowed_nations_list = []
        self.allowed_nations_list = allowed_nations_list
        if computer_player_list is None:
            computer_player_list = []
        self.computer_player_list = computer_player_list
        if ai_allies_list is None:
            ai_allies_list = []
        self.ai_allies_list = ai_allies_list
        self.victory_type = victory_type
        if cannot_win_list is None:
            cannot_win_list = []
        self.cannot_win_list = cannot_win_list
        if victory_point_provinces is None:
            victory_point_provinces = []
        self.victory_point_provinces = victory_point_provinces

        # Start location data/commands
        if start_locations is None:
            start_locations = []
        self.start_locations = start_locations
        if no_start_locations is None:
            no_start_locations = []
        self.no_start_locations = no_start_locations
        if special_start_locations is None:
            special_start_locations = []
        self.special_start_locations = special_start_locations
        if team_start_locations is None:
            team_start_locations = []
        self.team_start_locations = team_start_locations

        # Meta data (for later)
        self.seed = self.settings.seed
        self.layout = None
        self.surface_pixel_map = None
        self.surface_pixel_owner_list = None
        self.ug_pixel_map = None
        self.ug_pixel_owner_list = None
        self.height_map = None
        self.min_dist = None

    # Printing the class returns this
    def __str__(self):
        return '%s : %s' % (self.map_title, self.description)

    # Instructs the map class to load in an existing .map file.
    # This also creates province, army and pretender class lists.
    def read_map_file(self, filepath):

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

    # Instructs the map class to print a .map file with a specific name (should really be the map name)
    def make_map_file(self, filepath=None):

        if filepath is None:
            filepath = '%s.map' % self.map_title

        with open(filepath, 'w') as f:

            # General map info
            f.write('--This map file was made using DreamAtlas\n\n')
            f.write('--General Map Information\n')
            f.write('#dom2title %s\n' % self.map_title)
            f.write('#imagefile %s\n' % self.image_file)
            f.write('#winterimagefile %s\n' % self.winter_image_file)
            f.write('#mapsize %s %s\n' % (self.map_size[0], self.map_size[1]))
            # f.write('#wraparound\n')
            if not self.capital_names:
                f.write('#nohomelandnames')
            if self.scenario:
                f.write('#scenario\n')
            if self.dom_version is not None:
                f.write('#domversion %s\n' % self.dom_version)
            f.write('#maptextcol ' + ' '.join(map(str, self.map_text_colour)) + '\n')
            f.write('#mapdomcol ' + ' '.join(map(str, self.map_dom_colour)) + '\n')
            if self.max_sail_distance is not None:
                f.write('#saildist %s\n' % self.max_sail_distance)
            if self.magic_sites is not None:
                f.write('#features %s\n' % self.magic_sites)
            if self.victory_type is not None:
                f.write('#victorycondition %s %s\n' % (self.victory_type[0], self.victory_type[1]))
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

            # Start info
            f.write('\n--Province start info\n')
            if len(self.start_locations) != 0:
                for entry in range(len(self.start_locations)):
                    f.write('#start %s\n' % self.start_locations[entry])
            if len(self.no_start_locations) != 0:
                for entry in range(len(self.no_start_locations)):
                    f.write('#nostart %s\n' % self.no_start_locations[entry])
            if len(self.special_start_locations) != 0:
                for entry in range(len(self.special_start_locations)):
                    f.write('#specstart ' + ' '.join(map(str, self.special_start_locations[entry])) + '\n')
            if len(self.team_start_locations) != 0:
                for entry in range(len(self.team_start_locations)):
                    f.write('#teamstart ' + ' '.join(map(str, self.team_start_locations[entry])) + '\n')

            # Unique province info
            f.write('\n--Unique province names\n')
            if len(self.victory_point_provinces) != 0:
                for entry in range(len(self.victory_point_provinces)):
                    f.write('#victorypoints ' + ' '.join(map(str, self.victory_point_provinces[entry])) + '\n')
            if len(self.province_names_list) != 0:
                for entry in range(len(self.province_names_list)):
                    f.write('#landname ' + ' '.join(map(str, self.province_names_list[entry])) + '\n')

            # Terrain info
            f.write('\n--Terrain info\n')
            if len(self.terrain_list) != 0:
                for entry in range(len(self.terrain_list)):
                    f.write('#terrain ' + ' '.join(map(str, self.terrain_list[entry])) + '\n')

            # Neighbour info
            f.write('\n--Neighbour info\n')
            if len(self.neighbour_list) != 0:
                for entry in range(len(self.neighbour_list)):
                    f.write('#neighbour ' + ' '.join(map(str, self.neighbour_list[entry])) + '\n')
            if len(self.special_neighbour_list) != 0:
                for entry in range(len(self.special_neighbour_list)):
                    f.write('#neighbourspec ' + ' '.join(map(str, self.special_neighbour_list[entry])) + '\n')

            # Pixel ownership info
            f.write('\n--Pixel ownership info\n')
            if len(self.pixel_owner_list) != 0:
                for entry in range(len(self.pixel_owner_list)):
                    f.write('#pb ' + ' '.join(map(str, self.pixel_owner_list[entry])) + '\n')

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

        self.min_dist = 50.000

    def make_d6m(self, filepath=None):

        # Open d6m class file
        # Format is little endian binary which requires data to be converted
        with open(filepath, "wb") as f:

            # Write headline map data
            f.write(struct.pack("<iiiiqhii", 898933, 3, int(self.map_size[0]), int(self.map_size[1]), 0,
                                int((self.min_dist % 1.0) * 10000), int(self.min_dist),
                                int(len(self.province_list))))

            # Write pixel positions of each 'capital' (fort) and the 'spec' (if its deep sea, unknown why this is)
            for province in self.province_list:
                x, y = province.coordinates
                f.write(struct.pack("<hhq", int(x), int(y), province.terrain_int & 2052))

            # Write height for each pixel
            for height in np.ndarray.flatten(self.height_map, order='F'):
                f.write(struct.pack("<h", int(height)))
                # f.write(struct.pack("<h", rd.randint(-1000, 1000)))

            # Write ownership for each pixel
            for owner in np.ndarray.flatten(self.pixel_map, order='F'):
                f.write(struct.pack("<h", int(owner)))

            # Write final 'magic number' (allows dom6.exe to recognise the file)
            f.write(struct.pack("<i", 1155))
