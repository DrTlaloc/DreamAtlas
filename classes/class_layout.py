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
            if (0 <= i_coord[0] < map_size[0]) and (
                    0 <= i_coord[1] < map_size[1]):  # only do this for nodes in the graph
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
        self.seed = map_class.seed

        # Region level layout - supersedes planes
        self.region_graph = None
        self.region_coordinates = None
        self.region_darts = None
        self.region_edge_types = None
        self.region_rotation = None
        self.anchor_set = {0}

        # Province level layout - list per plane
        self.graph = [{} for _ in range(10)]
        self.coordinates = [{} for _ in range(10)]
        self.darts = [{} for _ in range(10)]
        self.edge_types = [[] for _ in range(10)]
        self.neighbours = [[] for _ in range(10)]
        self.special_neighbours = [[] for _ in range(10)]
        self.gates = [[] for _ in range(10)]
        self.min_dist = [np.Inf for _ in range(10)]

    def generate_region_layout(self,
                               seed: int = None):
        dibber(self, seed)  # Setting random seed

        map_size = self.map.map_size[1]
        nation_list = self.map.settings.nations
        player_neighbours = self.map.settings.player_neighbours

        # Select a player layout and build the basic graph
        graph = rd.choice(DATASET_GRAPHS[len(nation_list)][player_neighbours])
        ntx_graph = ntx.Graph(incoming_graph_data=graph)
        graph, coordinates, darts, _ = minor_graph_embedding(ntx_graph, map_size, 0.01)

        weights = {}
        for i in graph:
            weights[i] = 1
        graph, coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, map_size,
                                                               ratios=(0.5, 2), iterations=500)

        # Now add periphery regions in between the players
        done_edges = {(0, 0)}
        rotation = {}
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
                    i_j_vector = np.subtract(coordinates[j] + np.multiply(darts[i][connection], map_size),
                                             coordinates[i])
                    p_coords = coordinates[i] + 0.5 * i_j_vector
                    pi_dart = [0, 0]
                    pj_dart = [0, 0]

                    for axis in range(2):
                        if darts[i][connection][axis] == 1:
                            if p_coords[axis] < map_size[axis]:  # 1 s
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
                    coordinates[p] = np.mod(p_coords, map_size)
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
        for i in range(self.map.settings.throne_count):  # Adding the throne to the dicts
            graph[t] = []
            coordinates[t] = np.mod(p_coords, map_size)
            darts[t] = []
            rotation[t] = 0

        self.region_graph = graph
        self.region_coordinates = coordinates
        self.region_darts = darts
        self.region_edge_types = None
        self.region_rotation = rotation

    def generate_province_layout(self,
                                 plane: int,
                                 seed: int = None):
        dibber(self, seed)  # Setting random seed

        province_list = self.map.province_list[plane]
        map_size = self.map.map_size[plane]

        weights = {}
        for province in self.map.province_list[plane]:
            weights[province.index] = province.size

        lloyd_points = np.empty((len(province_list), 2))  # lloyd relaxation step
        for index in range(len(province_list)):
            lloyd_points[index] = province_list[index].coordinates
        lloyd = LloydRelaxation(lloyd_points)
        lloyd.relax()
        lloyd.relax()
        lloyd.relax()
        lloyd_points = lloyd.get_points()
        for index in range(len(province_list)):
            province_list[index].coordinates = lloyd_points[index]

        graph, coordinates, darts = make_delaunay_graph(province_list, map_size)
        graph, coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, map_size,
                                                               ratios=(0.8, 0.05), iterations=1000)

        for province in province_list:
            province.coordinates = coordinates[province.index]

        self.graph[plane] = graph
        self.coordinates[plane] = coordinates
        self.darts[plane] = darts

    def generate_neighbours(self,
                            plane: int):

        done_provinces = {0}
        self.neighbours[plane] = []
        self.min_dist[plane] = np.Inf

        for i in self.graph[plane]:  # Assigning all graph edges as neighbours
            done_provinces.add(i)
            for j in self.graph[plane][i]:
                if j not in done_provinces:
                    self.neighbours[plane].append([i, j])
                    dist = np.linalg.norm(
                        self.coordinates[plane][j] + np.multiply(self.darts[plane][i][self.graph[plane][i].index(j)],
                                                                 self.map.map_size[plane]) - self.coordinates[plane][i])
                    if dist < self.min_dist[plane]:
                        self.min_dist[plane] = dist

    def generate_special_neighbours(self,
                                    plane: int,
                                    seed: int = None):
        dibber(self, seed)  # Setting random seed

        if not self.neighbours[plane]:
            return Exception('No neighbours')
        self.special_neighbours[plane] = []
        index_2_prov = {}
        for province in self.map.province_list[plane]:
            index_2_prov[province.index] = province

        for i, j in self.neighbours[plane]:  # Randomly assigns special connections (will be improved in v1.1)
            i_j_provs = [index_2_prov[i], index_2_prov[j]]
            choice = int(rd.choices(SPECIAL_NEIGHBOUR, NEIGHBOUR_SPECIAL_WEIGHTS)[0][0])
            if choice != 0:
                for index in range(2):
                    if i_j_provs[index].capital_location:  # Ignore caps
                        break
                    elif i_j_provs[index].terrain_int & 4 == 4:  # Ignore UW
                        break
                    elif i_j_provs[index].terrain_int & 4096 == 4096:  # Ignore cave
                        break
                    elif i_j_provs[index].terrain_int & 68719476736 == 68719476736:  # if cave wall
                        self.special_neighbours[plane].append([i, j, 4])
                        break
                    else:
                        if (choice == 1 or choice == 4) and not (i_j_provs[index].terrain_int & 8388608 == 8388608):
                            i_j_provs[index].terrain_int += 8388608
                        self.special_neighbours[plane].append([i, j, choice])

    def generate_gates(self,
                       seed: int = None):
        dibber(self, seed)  # Setting random seed

        # index_2_prov = {}
        #
        # for plane in range(10):
        #     if not self.map.province_list[plane]:
        #         for province in self.map.province_list[plane]:
        #             index_2_prov[province.index] = province
        #             index_2_region[province.index] = province.parent_region
        #
        # self.gates = 1

    # def plot(self, graph, coordinates, ax=None, real_size=None):
    #
    #     if ax is None:
    #         _ = plt.figure()
    #         ax = plt.axes()
    #
    #     if real_size is None:
    #         real_size = np.Inf
    #
    #     for vertex in range(len(graph)):
    #         x0, y0 = coordinates[vertex + 1]
    #         for edge in graph[vertex + 1]:
    #             x1, y1 = coordinates[edge]
    #             ax.plot([x0, x1], [y0, y1], 'k-')
    #
    #     for vertex in range(len(graph)):
    #         x0, y0 = coordinates[vertex + 1]
    #         if vertex > real_size - 1:
    #             ax.plot(x0, y0, 'go')
    #             ax.text(x0, y0, str(vertex + 1))
    #         else:
    #             ax.plot(x0, y0, 'ro')
    #             ax.text(x0, y0, str(vertex + 1))
    #
    #     ax.set(xlim=(0, 2000), ylim=(0, 1000))
