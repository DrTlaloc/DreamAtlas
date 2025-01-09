import numpy as np

from . import *


def less_first(a, b):
    return [a, b] if a < b else [b, a]


def make_delaunay_graph(province_list: list[Province],
                        map_size: np.array,
                        neighbours: list = NEIGHBOURS_FULL):

    graph, coordinates, darts = dict(), dict(), dict()
    for province in province_list:  # Set up the dicts and assign coordinates
        index = province.index
        graph[index], coordinates[index], darts[index] = list(), np.asarray(province.coordinates, dtype=np.float32), list()

    points, key_list, counter = list(), dict(), 0
    for province in province_list:  # Set up the virtual points on the toroidal plane
        for n in neighbours:
            x, y = np.asarray(province.coordinates + n * map_size)
            points.append([x, y])
            key_list[counter] = province.index
            counter += 1

    tri = sc.spatial.Delaunay(np.array(points), qhull_options='QJ')

    list_of_edges = list()
    for triangle in tri.simplices:
        for e1, e2 in [[0, 1], [1, 2], [2, 0]]:  # for all edges of triangle
            list_of_edges.append(less_first(triangle[e1], triangle[e2]))  # always lesser index first

    for p1, p2 in np.unique(list_of_edges, axis=0):  # remove duplicates
        index1, index2 = key_list[p1], key_list[p2]
        i_c = tri.points[p1]
        if (0 <= i_c[0] < map_size[0]) and (0 <= i_c[1] < map_size[1]):  # only do this for nodes in the map
            graph[index1].append(index2)
            graph[index2].append(index1)

            j_c = tri.points[p2]

            dart = [0, 0]
            for axis in range(2):
                if j_c[axis] < 0:
                    dart[axis] = -1
                elif j_c[axis] >= map_size[axis]:
                    dart[axis] = 1

            darts[index1].append(dart)
            darts[index2].append([-dart[0], -dart[1]])

    return graph, coordinates, darts


class DominionsLayout:

    def __init__(self, map_class):  # This class handles layout

        self.map = map_class
        self.seed = map_class.seed
        self.map_size = map_class.map_size

        # Region level layout - supersedes planes
        self.region_planes = None
        self.region_types = None
        self.region_graph = None
        self.region_coordinates = None
        self.region_darts = None

        # Province level layout - list per plane
        self.graph = [dict() for _ in range(10)]
        self.coordinates = [dict() for _ in range(10)]
        self.darts = [dict() for _ in range(10)]
        self.edge_types = [list() for _ in range(10)]
        self.neighbours = [list() for _ in range(10)]
        self.special_neighbours = [list() for _ in range(10)]
        self.gates = [list() for _ in range(10)]
        self.min_dist = [np.Inf for _ in range(10)]

    def generate_region_layout(self,
                               players_teams: list[list[int, int]],
                               player_connections: int,
                               periphery_connections: int,
                               throne_regions: int,
                               water_regions: int,
                               cave_regions: int,
                               vast_regions: int,
                               blocker_regions: int,
                               map_size: np.array,
                               seed: int = None):
        dibber(self, seed)  # Setting random seed

        teams = dict()
        for player, team in players_teams:  # Analyse player teams
            if team not in teams:
                teams[team] = [player]
            else:
                teams[team].append(player)

        num_regions = (1 + len(teams) * int(0.5 * player_connections + 1) + throne_regions + water_regions + cave_regions + vast_regions + blocker_regions)
        region_types = [None] * num_regions
        region_planes = [None] * num_regions
        graph = copy(rd.choice(DATASET_GRAPHS[len(teams)][player_connections]))  # Select an initial layout

        done_edges, p, periphery_set = set(), len(graph), list()  # Now add periphery regions in between the players
        for i in range(1, 1 + len(graph)):
            region_planes[i] = 1
            if Nation(players_teams[i-1]).home_plane == 2:
                region_planes[i] = 2
            region_types[i] = 0
            for ii, j in enumerate(graph[i]):
                if (i, j) not in done_edges:
                    p += 1
                    done_edges.add((p, i))
                    done_edges.add((j, p))
                    graph[p] = [i, j]  # Adding the periphery to the dicts
                    graph[i][ii] = p  # Modifying the existing connections/darts
                    graph[j][graph[j].index(i)] = p
                    region_planes[p] = 1
                    region_types[p] = 1
                    periphery_set.append(p)

        coordinates, darts = embed_region_graph(graph, map_size, 100, seed)

        weights = dict()
        for i in range(len(region_types)):
            weights[i] = 1

        coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, map_size, ratios=np.asarray((0.1, 0.5, 20), dtype=np.float32), iterations=50)  # quick pass to clean up the embedding
        faces, centroids = find_graph_faces(graph, coordinates, darts, map_size)

        if throne_regions > len(centroids):
            raise Exception("\033[31m" + "Error: more thrones (%i) than good throne locations (%i)\x1b[0m" % (throne_regions, len(centroids)))

        codebook, distortion = sc.cluster.vq.kmeans(obs=np.array(centroids, dtype=np.float32), k_or_guess=throne_regions)

        # Adding the throne regions
        i = len(graph)
        for coordinate in codebook:
            i += 1
            closest_distance = np.inf
            for j, centroid in enumerate(centroids):
                distance = np.linalg.norm(np.subtract(centroid, coordinate))
                if distance < closest_distance:
                    best_centroid = centroid
                    closest_distance = distance
                    face = faces[j]
            centroids.remove(best_centroid)

            region_planes[i] = 1
            region_types[i] = 2
            graph[i] = []
            coordinates[i] = best_centroid
            darts[i] = []

            # face_set = set()
            # for a, b in face:
            #     face_set.add(a)
            #     face_set.add(b)
            # for k in face_set:
            #     graph[i].append(k)
            #     darts[i].append([0, 0])
            #     graph[k].append(i)
            #     darts[k].append([0, 0])

        # Add water regions

        # Add cave regions
        cave_locations = rd.sample(centroids, cave_regions)
        ii = 1 + len(graph)
        for i in range(cave_regions):
            region_planes[ii+i] = 2
            region_types[ii+i] = 4
            graph[ii+i] = []
            coordinates[ii+i] = cave_locations[i]
            darts[ii+i] = []

            for _ in range(2):
                j = rd.choice(periphery_set)
                periphery_set.remove(j)
                graph[ii+i].append(j)
                graph[j].append(ii+i)
                darts[ii + i].append([0, 0])
                darts[j].append([0, 0])

        # Add vast regions

        # Add blocker regions
        ratio = map_size[0] / map_size[1]
        l1 = int(1+ np.sqrt(blocker_regions / ratio))
        l2 = int(1 + l1 * ratio)
        x = np.linspace(10, map_size[0]-10, l2)
        y = np.linspace(10, map_size[1]-10, l1)
        x, y = np.meshgrid(x, y)
        wall_coordinates = np.vstack([x.ravel(), y.ravel()])

        ii = 1 + len(graph)
        for i in range(blocker_regions):
            region_planes[ii + i] = 2
            region_types[ii+i] = 6
            graph[ii+i] = []
            coordinates[ii+i] = wall_coordinates[:, i]
            darts[ii+i] = []

        # coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, map_size, ratios=np.asarray((0.1, 0.2, 30), dtype=np.float32), iterations=0)  # final pass to clean up the embedding
        self.region_planes = region_planes
        self.region_types = region_types
        self.region_graph = graph
        self.region_coordinates = coordinates
        self.region_darts = darts

    def generate_province_layout(self,
                                 plane: int,
                                 seed: int = None):
        dibber(self, seed)  # Setting random seed

        province_list = self.map.province_list[plane]
        map_size = self.map.map_size[plane]
        base_length = 0.15 * np.sqrt(map_size[0] * map_size[1] / len(province_list))

        weights = dict()
        for i, province in enumerate(province_list):
            weights[province.index] = province.size

        graph, coordinates, darts = make_delaunay_graph(province_list, map_size)
        coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, map_size, ratios=np.asarray((0.25, 0.9, base_length), dtype=np.float32), iterations=1000)

        self.graph[plane] = graph
        self.coordinates[plane] = coordinates
        self.darts[plane] = darts

    def generate_neighbours(self, plane: int):

        done_provinces = set()
        self.neighbours[plane] = list()
        self.min_dist[plane] = np.Inf

        for i in self.graph[plane]:  # Assigning all graph edges as neighbours
            done_provinces.add(i)
            for ii, j in enumerate(self.graph[plane][i]):
                if j not in done_provinces:
                    self.neighbours[plane].append([i, j])
                    dist = np.linalg.norm(self.coordinates[plane][j] + np.multiply(self.darts[plane][i][ii], self.map.map_size[plane]) - self.coordinates[plane][i])
                    if dist < self.min_dist[plane]:
                        self.min_dist[plane] = dist

    def generate_special_neighbours(self,
                                    plane: int,
                                    seed: int = None):
        dibber(self, seed)  # Setting random seed

        if not self.neighbours[plane]:
            raise Exception('No neighbours')
        self.special_neighbours[plane] = list()
        index_2_prov = dict()
        for province in self.map.province_list[plane]:
            index_2_prov[province.index] = province

        for i, j in self.neighbours[plane]:  # Randomly assigns special connections (will be improved in v1.1)
            i_j_provs = [index_2_prov[i], index_2_prov[j]]
            choice = int(rd.choices(SPECIAL_NEIGHBOUR, NEIGHBOUR_SPECIAL_WEIGHTS)[0][0])
            if choice != 0:
                fail = False
                for index in range(2):
                    ti = i_j_provs[index].terrain_int
                    if i_j_provs[index].capital_location:  # Ignore caps
                        fail = True
                    elif has_terrain(ti, 4):
                        fail = True
                    elif has_terrain(ti, 4096):
                        fail = True
                    elif has_terrain(ti, 68719476736):  # if cave wall
                        self.special_neighbours[plane].append([i, j, 4])
                        fail = True
                    elif (choice == 33 or choice == 36) and not has_terrain(ti, 8388608):
                        i_j_provs[index].terrain_int += 8388608
                if not fail:
                    self.special_neighbours[plane].append([i, j, choice])

    def generate_gates(self, all_regions, seed: int = None):
        dibber(self, seed)  # Setting random seed
        self.gates = [[] for _ in range(10)]
        gate = 1
        for ii, i in enumerate(self.region_graph):
            i_region = all_regions[ii]
            if self.region_planes[i] == 2 and self.region_types[i] != 6:
                gate_connections = list()
                for j in self.region_graph[i]:
                    if self.region_planes[j] == 1:
                        gate_connections.append(j)

                if self.region_types[i] == 0:
                    gate_connections = gate_connections[0:3]

                for iii, j in enumerate(gate_connections):
                    i_province = i_region.provinces[iii]
                    j_province = rd.choice(all_regions[j].provinces)

                    self.gates[1].append([j_province.index, gate])
                    self.gates[2].append([i_province.index, gate])
                    gate += 1

    def plot(self):

        fig, axs = plt.subplots(3, 1)
        ax_regions = axs[0]
        ax_provinces = axs[1:]

        # Plot regions
        virtual_graph, virtual_coordinates = make_virtual_graph(self.region_graph, self.region_coordinates, self.region_darts, self.map_size[1])
        done_edges = set()
        for i in virtual_graph:  # region connections
            x0, y0 = virtual_coordinates[i]
            for j in virtual_graph[i]:
                if (i, j) not in done_edges:
                    done_edges.add((j, i))
                    x1, y1 = virtual_coordinates[j]
                    colour = 'k-'
                    if i in self.region_types:
                        if self.region_types[i] == 4:
                            colour = 'k--'
                    ax_regions.plot([x0, x1], [y0, y1], colour)

        region_colours = ['g*', 'rD', 'y^', 'bo', 'rv', 'ms', 'kX']
        for i in self.region_graph:
            x0, y0 = self.region_coordinates[i]
            ax_regions.plot(x0, y0, region_colours[self.region_types[i]])
            ax_regions.text(x0, y0, str(i))
        ax_regions.set(xlim=(0, self.map_size[1][0]), ylim=(0, self.map_size[1][1]))

        # Plot provinces
        for i, plane in enumerate(self.map.planes):
            ax = ax_provinces[i]
            virtual_graph, virtual_coordinates = make_virtual_graph(self.graph[plane], self.coordinates[plane], self.darts[plane], self.map.map_size[plane])
            for j in virtual_graph:  # region connections
                x0, y0 = virtual_coordinates[j]
                for k in virtual_graph[j]:
                    x1, y1 = virtual_coordinates[k]
                    ax.plot([x0, x1], [y0, y1], 'k-')

            for j in self.graph[plane]:
                x0, y0 = self.coordinates[plane][j]
                ax.plot(x0, y0, 'ro')
                ax.text(x0, y0, str(j))
            ax.set(xlim=(0, self.map_size[plane][0]), ylim=(0, self.map_size[plane][1]))

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
