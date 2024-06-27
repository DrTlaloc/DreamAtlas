import numpy as np

from . import *


def make_delaunay_graph(province_list: list[Province, ...],
                        map_size: tuple[int, int],
                        wraparound: tuple[bool, bool] = (True, True)):

    graph = {}
    coordinates = {}
    darts = {}

    for province in province_list:  # Set up the dicts and assign coordinates
        index = province.index
        x, y = province.coordinates
        graph[index] = []
        coordinates[index] = [x, y]
        darts[index] = []

    points = []
    key_list = {}
    counter = 0
    for province in province_list:  # Set up the virtual points on the toroidal plane
        index = province.index
        x0, y0 = province.coordinates
        for neighbour in NEIGHBOURS_FULL:
            x = x0 + neighbour[0] * map_size[0]
            y = y0 + neighbour[1] * map_size[1]
            if (-0.25 * map_size[0] <= x < 1.25 * map_size[0]) and (-0.25 * map_size[1] <= y < 1.25 * map_size[1]):
                points.append([x, y])
                key_list[counter] = index
                counter += 1

    def less_first(a, b):
        return [a, b] if a < b else [b, a]

    tri = sc.spatial.Delaunay(np.array(points))

    list_of_edges = []
    for triangle in tri.simplices:
        for e1, e2 in [[0, 1], [1, 2], [2, 0]]:  # for all edges of triangle
            list_of_edges.append(less_first(triangle[e1], triangle[e2]))  # always lesser index first
    array_of_edges = np.unique(list_of_edges, axis=0)  # remove duplicates

    done_edges = []
    for p1, p2 in array_of_edges:
        index1 = key_list[p1]
        index2 = key_list[p2]
        if [index1, index2] not in done_edges:

            i_coord = tri.points[p1]
            j_coord = tri.points[p2]
            if (0 <= i_coord[0] < map_size[0]) and (0 <= i_coord[1] < map_size[1]):  # only do this for nodes in the graph
                done_edges.append([index2, index1])
                graph[index1].append(index2)
                graph[index2].append(index1)

                dart = [0, 0]
                for axis in range(2):
                    if j_coord[axis] < 0:
                        dart[axis] = -1
                    elif j_coord[axis] >= map_size[axis]:
                        dart[axis] = 1

                darts[index1].append(dart)
                darts[index2].append(np.negative(dart))

    return graph, coordinates, darts


class DominionsLayout:

    def __init__(self,
                 map_class: DominionsMap):  # This class handles layout

        self.map = map_class
        self.settings = map_class.settings
        self.seed = map_class.seed
        self.map_size = map_class.map_size

        # Region level layout
        self.region_graph = None
        self.region_coordinates = None
        self.region_darts = None
        self.region_edge_types = None
        self.region_rotation = None
        self.anchor_set = {0}

        # Surface province level layout
        self.surface_graph = None
        self.surface_coordinates = None
        self.surface_darts = None
        self.surface_edge_types = None

        # Underground province level layout
        self.ug_graph = None
        self.ug_coordinates = None
        self.ug_darts = None
        self.ug_edge_types = None

    def generate_region_layout(self,
                               seed: int = None):
        dibber(self, seed)  # Setting random seed

        nation_list = self.settings.nations
        player_neighbours = self.settings.player_neighbours

        rotation = {}

        # Select a player layout and build the basic graph
        graph = rd.choice(DATASET_GRAPHS[len(nation_list)][player_neighbours])
        ntx_graph = ntx.Graph(incoming_graph_data=graph)
        graph, coordinates, darts, _ = minor_graph_embedding(ntx_graph, self.map_size, 0.01)

        weights = {}
        for i in graph:
            weights[i] = 1
        graph, coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, self.map_size,
                                                               ratios=(0.03, 2), iterations=200)

        # Now add periphery regions in between the players
        done_edges = {(0, 0)}
        p = len(graph)
        for i in range(1, 1 + len(nation_list)):
            for connection in range(len(graph[i])):
                j = graph[i][connection]
                edge = (i, j)
                if edge not in done_edges:
                    p += 1
                    done_edges.add((p, i))
                    done_edges.add((j, p))

                    # Finding where the peripheral should be
                    i_j_vector = np.subtract(coordinates[j] + np.multiply(darts[i][connection], self.map_size),
                                             coordinates[i])
                    p_coords = coordinates[i] + 0.5 * i_j_vector
                    pi_dart = [0, 0]
                    pj_dart = [0, 0]

                    for axis in range(2):
                        if darts[i][connection][axis] == 1:
                            if p_coords[axis] < self.map_size[axis]:  # 1 s
                                pi_dart[axis] = 0
                                pj_dart[axis] = -1
                            else:  # 1 o
                                pi_dart[axis] = 1
                                pj_dart[axis] = 0
                        elif darts[i][connection][axis] == 1:
                            if p_coords[axis] >= 0:  # -1 s
                                pi_dart[axis] = 0
                                pj_dart[axis] = 1
                            else:  # -1 o
                                pi_dart[axis] = -1
                                pj_dart[axis] = 0

                    # Adding the periphery to the dicts
                    graph[p] = [i, j]
                    coordinates[p] = np.mod(p_coords, self.map_size)
                    darts[p] = [[pi_dart], [pj_dart]]
                    rotation[p] = 90 - np.angle([i_j_vector[0] + i_j_vector[1] * 1j], deg=True)

                    # Modifying the existing connections/darts
                    graph[i][connection] = p
                    darts[i][connection] = np.negative(pi_dart)
                    for o in range(len(graph[j])):
                        if graph[j][o] == i:
                            graph[j][o] = p
                            darts[j][o] = np.negative(pj_dart)

        # Finally add thrones between peripheries with shared spaces
        t = len(graph)
        for i in range(self.settings.throne_count):  # Adding the throne to the dicts
            graph[t] = []
            coordinates[t] = np.mod(p_coords, self.map_size)
            darts[t] = []
            rotation[t] = 0

        self.region_graph = graph
        self.region_coordinates = coordinates
        self.region_darts = darts
        self.region_edge_types = None
        self.region_rotation = rotation

    def generate_province_layout(self,
                                 seed: int = None):
        dibber(self, seed)  # Setting random seed

        surface_province_list = []
        surface_weights = {}
        ug_province_list = []
        ug_weights = {}

        for province in self.map.province_list:
            if province.plane == 1:
                surface_province_list.append(province)
                surface_weights[province.index] = province.size

            elif province.plane == 2:
                ug_province_list.append(province)
                ug_weights[province.index] = province.size

        # Surface province level layout
        surface_lloyd_points = np.empty((len(surface_province_list), 2))
        for index in range(len(surface_province_list)):
            surface_lloyd_points[index] = surface_province_list[index].coordinates
        lloyd = LloydRelaxation(surface_lloyd_points)
        lloyd.relax()
        lloyd.relax()
        surface_lloyd_points = lloyd.get_points()
        for index in range(len(surface_province_list)):
            surface_province_list[index].coordinates = surface_lloyd_points[index]

        surface_graph, surface_coordinates, surface_darts = make_delaunay_graph(surface_province_list, self.map_size)
        self.surface_graph, self.surface_coordinates, self.surface_darts = spring_electron_adjustment(surface_graph, surface_coordinates, surface_darts, surface_weights, self.map_size, ratios=(0.01, 2), iterations=1000)

        for province in surface_province_list:
            province.coordinates = self.surface_coordinates[province.index]

        self.surface_graph, self.surface_coordinates, self.surface_darts = make_delaunay_graph(surface_province_list, self.map_size)

        # Underground province level layout
        ug_graph, ug_coordinates, ug_darts = make_delaunay_graph(ug_province_list, self.map_size)
        self.ug_graph, self.ug_coordinates, self.ug_darts = spring_electron_adjustment(ug_graph, ug_coordinates, ug_darts, ug_weights, self.map_size, ratios=(0.01, 2), iterations=200)

    def generate_special_neighbours_gates(self,
                                  seed: int = None):
        dibber(self, seed)  # Setting random seed

        self.surface_edge_types = None
        self.ug_edge_types = None

    def get_neighbour_lists(self):

        done_edges = {{-1, -1}}
        neighbour_list = []
        special_neighbour_list = []

        for i in self.surface_graph:  # Assigning all graph edges as neighbours
            for j in self.surface_graph[i]:
                if {i, j} not in done_edges:
                    done_edges.add({i, j})
                    neighbour_list.append([i, j])

                    if {i, j} in self.special_connections:  # Assigning special connections (rivers, gates, mountains etc)
                        type = 1
                        special_neighbour_list.append([i, j, type])

        return neighbour_list, special_neighbour_list
