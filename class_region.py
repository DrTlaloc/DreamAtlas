# Imports all the DreamAtlas functionality and dependencies
from . import *


class Region:

    def __init__(self,
                 index: int = None,
                 nations: list = None,
                 region_type: str = None,
                 plane: int = None,
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

        self.plane = plane
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

    def generate_graph(self,
                       seed: int = None):
        dibber(self, seed)
        self.graph = {0: []}
        self.provinces = []

        # Loading constants from settings file
        variance = self.settings.variance
        spread_range = variance * self.settings.spread * PI_2 / self.settings.cap_connections
        base_radius = self.settings.base_radius

        # Generating the anchor province
        new_province = Province(index=0, plane=self.plane, coordinates=[0, 0])

        if self.is_homeland:
            self.anchor_connections = self.settings.cap_connections
            extra_provinces = self.settings.homeland_size - self.settings.cap_connections - 1
            new_province.capital_location = True
            new_province.special_capital = self.nations
        elif self.is_periphery:
            self.anchor_connections = self.settings.periphery_size - 1
            extra_provinces = self.settings.periphery_size - 4
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
                new_province = Province(index=index + 1, plane=self.plane, coordinates=[x, y])
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
                new_province = Province(index=index, plane=self.plane, coordinates=[x, y])
                self.provinces.append(new_province)

    def generate_terrain(self,
                         seed: int = None):
        dibber(self, seed)

        # Loading terrain info
        if self.is_homeland:
            terrain_pref = self.nations[0].terrain_profile
            layout = self.nations[0].layout
        elif self.is_periphery:
            terrain_pref, layout = nations_2_periphery(self.nations)
        elif self.is_throne:
            terrain_pref, layout = TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND

        # Apply the terrain and land/sea/cave tags to each province
        for index in range(len(self.provinces)):
            province = self.provinces[index]
            if province.capital_location:  # cap
                province.terrain_int = self.nations[0].cap_terrain
                province.plane = self.nations[0].home_plane
                province.size = 1.5
            elif province.index <= self.anchor_connections:  # cap circle
                province.terrain_int = rd.choices(TERRAIN_PREF_BITS, weights=terrain_pref, k=1)[0]
                province.size = 1
                if not self.is_throne:
                    province.plane = self.nations[0].home_plane
                    if index / self.anchor_connections > layout[0]:  # land/sea
                        province.terrain_int += 4
            else:  # other homeland provinces
                province.terrain_int = rd.choices(TERRAIN_PREF_BITS, weights=terrain_pref, k=1)[0]
                province.size = 1
                if rd.random() > layout[1]:  # land/sea
                    province.terrain_int += 4
                province.plane = 1

    def generate_population(self,
                            seed: int = None):  # Generates the population for the region
        dibber(self, seed)

        pop_balancing = self.settings.pop_balancing
        if not pop_balancing:  # No population balancing
            return

        total_pop = AGE_POPULATION_MODIFIERS[self.settings.age] * AVERAGE_POPULATION_SIZES[1] * len(self.provinces)

        for province in self.provinces:
            if province.capital_location:  # Assign capital population
                province.population = CAPITAL_POPULATION
                total_pop -= AGE_POPULATION_MODIFIERS[self.settings.age] * AVERAGE_POPULATION_SIZES[1]
                continue
            if pop_balancing:  # Soft population balancing
                this_pop = 2 * rd.random() * AVERAGE_POPULATION_SIZES[1]
            else:  # Hard population balancing
                this_pop = 2 * rd.random() * AVERAGE_POPULATION_SIZES[1]
            province.population = this_pop
            total_pop -= this_pop

    def embed_region(self,
                     global_coordinates: list,
                     initial_index: int,
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
            province.index = initial_index
            province.parent_region = self.index
            initial_index += 1
