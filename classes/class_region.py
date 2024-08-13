from . import *


class Region:

    def __init__(self,
                 index: int = None,
                 nations: list = None,
                 region_type: str = None,
                 settings: DreamAtlasSettings = None,
                 seed: int = None):

        self.index = index
        if nations is None:
            nations = [0]
        self.nations = nations

        if region_type is None:
            region_type = REGION_TYPE[len(nations)]
        self.region_type = region_type
        self.is_throne = region_type == 'Throne'
        self.is_homeland = region_type == 'Homeland'
        self.is_periphery = region_type == 'Periphery'

        if settings is None:
            settings = DEFAULT_SETTINGS
        self.settings = settings
        if seed is None:
            seed = self.settings.seed
        self.seed = seed
        for nation in self.nations:  # Adjusts the seed based on the nation (so that every region isn't identical)
            self.seed *= nation.index

        self.graph = {}         # Graph is a dictionary for the province graph
        self.provinces = []     # Provinces is a list for the province classes in the homeland

        if self.is_homeland:  # Loading terrain/layout info
            self.terrain_pref, self.layout = self.nations[0].terrain_profile, self.nations[0].layout
        elif self.is_periphery:
            self.terrain_pref, self.layout = nations_2_periphery(self.nations)
        elif self.is_throne:
            self.terrain_pref, self.layout = TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND

    def generate_graph(self,
                       seed: int = None):
        dibber(self, seed)
        self.graph = {0: []}
        self.provinces = []

        # Loading constants from settings file
        variance = self.settings.variance
        spread_range = variance**2 * PI_2 / self.settings.cap_connections
        base_radius = self.settings.base_radius

        # Generating the anchor province
        new_province = Province(plane=1, coordinates=[0, 0])

        if self.is_homeland:
            self.anchor_connections = self.settings.cap_connections
            extra_provinces = self.settings.homeland_size - self.settings.cap_connections - 1
            new_province.capital_location = True
            new_province.special_capital = self.nations[0].index
            new_province.plane = self.nations[0].home_plane
        elif self.is_periphery:
            self.anchor_connections = self.settings.periphery_size - 1
            extra_provinces = self.settings.periphery_size - self.anchor_connections - 1
        elif self.is_throne:
            self.anchor_connections = 0
            extra_provinces = 0

        self.provinces.append(new_province)

        # Generate the anchor connections, rotating randomly, then adding some small random angle/radius change
        if self.anchor_connections > 0:
            angles = np.linspace(0, PI_2, self.anchor_connections, endpoint=False)
            angles += rd.uniform(0, variance * np.pi / self.anchor_connections)
            radii = [base_radius] * self.anchor_connections

            for index in range(self.anchor_connections):
                self.graph[0] = self.graph[0] + [index + 1]
                self.graph[index + 1] = [0]

                theta = angles[index] + rd.uniform(-spread_range, spread_range)
                radius = radii[index] + rd.uniform(-0.2 * variance, 0.2 * variance)
                x = radius * np.cos(theta)
                y = radius * np.sin(theta)
                new_province = Province(plane=1, coordinates=[x, y])
                if self.is_homeland:
                    new_province.plane = self.nations[0].home_plane
                self.provinces.append(new_province)

        # Place the remaining extra provinces attached to non-anchor provinces
        if extra_provinces > 0:
            for province in range(extra_provinces):
                anchor = 1 + rd.choice(range(self.anchor_connections))
                index = 2 + self.anchor_connections + province

                self.graph[anchor] = self.graph[anchor] + [index]
                self.graph[index] = [anchor]

                theta = angles[anchor - 1] + variance * rd.uniform(-np.pi, np.pi)
                radius = base_radius + rd.uniform(0, 0.3 * variance)
                x0, y0 = self.provinces[anchor].coordinates
                x = x0 + radius * np.cos(theta)
                y = y0 + radius * np.sin(theta)
                new_province = Province(plane=1, coordinates=[x, y])
                self.provinces.append(new_province)

    def generate_terrain(self,
                         seed: int = None):
        dibber(self, seed)

        # Apply the terrain and land/sea/cave tags to each province
        for index in range(len(self.provinces)):
            province = self.provinces[index]

            if province.capital_location:
                province.terrain_int += self.nations[0].cap_terrain  # Capital terrain
                province.terrain_int += 67108864  # Good start location
            else:
                province.terrain_int += 512  # No start location

                if index <= self.anchor_connections:  # cap circle
                    if not self.is_throne:
                        if index / self.anchor_connections > self.layout[0]:  # land/sea
                            province.terrain_int += 4
                else:  # other homeland provinces
                    if rd.random() > self.layout[1]:  # land/sea
                        province.terrain_int += 4

                choice = rd.choices(TERRAIN_PREF_BITS, weights=self.terrain_pref, k=1)[0]
                if province.terrain_int & 4 == 4:
                    if not (choice & 32 == 32 or choice & 64 == 64 or choice & 256 == 256):
                        province.terrain_int += choice
                else:
                    province.terrain_int += choice

                if self.is_throne:
                    province.terrain_int += 33554432  # Good throne location
                else:
                    province.terrain_int += 134217728  # Bad throne location

                if province.plane == 2:
                    province.terrain_int += 4096  # Cave layer
                    province.terrain_int += 576460752303423488  # Cave wall effect

    def generate_population(self,
                            seed: int = None):  # Generates the population for the region
        dibber(self, seed)

        pop_balancing = self.settings.pop_balancing
        if pop_balancing == 0:  # No population balancing
            return
        if pop_balancing == 2:  # Re-seed with same seed for all regions in this case
            dibber(self, self.settings.seed)

        split_pop = np.linspace(0, 1, 1 + len(self.provinces))
        for index in range(1, len(split_pop)-1):
            split_pop[index] += rd.uniform(-0.25/len(self.provinces), 0.25/len(self.provinces))
        new_pop = np.diff(np.multiply(split_pop, AGE_POPULATION_MODIFIERS[self.settings.age] * 10000 * len(self.provinces)))

        for index in range(len(self.provinces)):
            province = self.provinces[index]
            province.has_commands = True
            if province.capital_location:  # Assign capital population
                province.population = CAPITAL_POPULATION
            else:
                province.population = new_pop[index]

    def embed_region(self,
                     global_coordinates: list,
                     rotation: float,
                     scale: tuple[int, int],
                     map_size: list[int, int],
                     seed: int = None):  # Embeds the region in a global space
        dibber(self, seed)

        # Transforming each province from the local to global coordinate system
        radians = np.deg2rad(rotation)
        for province in self.provinces:
            x_province = province.coordinates[0] * np.cos(radians) + province.coordinates[1] * np.sin(radians)
            y_province = -province.coordinates[0] * np.sin(radians) + province.coordinates[1] * np.cos(radians)
            province.coordinates = [int(global_coordinates[0] + scale[0] * x_province) % map_size[0], int(global_coordinates[1] + scale[1] * y_province) % map_size[1]]
            province.parent_region = self.index
            province.size, province.shape = find_shape_size(province, self.settings)

    def plot(self,
             terrain: bool = True,
             population: bool = True):

        # Making the figures (graph, terrain, population)
        fig, axs = plt.subplots(1, 1 + terrain + population)
        ax_graph = axs[0]
        plot_size = [500, 500]
        z_graph = np.zeros(plot_size)
        if terrain:
            ax_terrain = axs[1]
            z_terrain = np.zeros(plot_size)
        if population:
            ax_population = axs[2]
            z_population = np.zeros(plot_size)

        # Make the contourf z objects to be plotted
        points = []
        for province in self.provinces:
            index = province.index
            x, y = province.coordinates
            points.append([index, x, y])

        pixel_map = find_pixel_ownership(points, plot_size, hwrap=False, vwrap=False, scale_down=8, minkowski_dist=3)
        for x in range(plot_size[0]):
            for y in range(plot_size[1]):
                this_index = pixel_map[x][y]
                z_graph[y][x] = this_index
                if terrain:
                    terrain_list = terrain_int2list(self.provinces[this_index - 1].terrain_int)
                    for terrain in terrain_list:
                        z_terrain[y][x] += TERRAIN_2_HEIGHTS_DICT[terrain]
                if population:
                    z_population[y][x] = self.provinces[this_index - 1].population

        # Plotting the contourf and the province border contour map
        levels = len(self.graph)
        ax_graph.imshow(z_graph, cmap=cm.Set1)
        ax_graph.contour(z_graph, levels=levels, colors=['white', ])
        ax_graph.set_title('Provinces')
        if terrain:
            ax_terrain.imshow(z_terrain, vmin=-200, vmax=600, cmap=cm.terrain)
            ax_terrain.contour(z_graph, levels=levels, colors=['white', ])
            ax_terrain.set_title('Terrain')
        if population:
            ax_population.imshow(z_population, vmin=0, vmax=45000, cmap=cm.YlGn)
            ax_population.contour(z_graph, levels=levels, colors=['white', ])
            ax_population.set_title('Population')

        name = ''
        for nation in self.nations:
            name = name + ' +' + nation.name
        fig.suptitle('%s Region' % name)

