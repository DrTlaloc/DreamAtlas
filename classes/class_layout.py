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
        coordinates[index] = [int(x), int(y)]
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
                darts[index2].append([-dart[0], -dart[1]])

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

        # Select a player layout and build the basic graph
        graph = copy(rd.choice(DATASET_GRAPHS[len(self.map.settings.nations)+len(self.map.settings.custom_nations)][self.map.settings.player_neighbours]))

        # Now add periphery regions in between the players
        done_edges, rotation, p = set(), dict(), len(graph)
        for i in range(1, 1 + len(graph)):
            for connection in range(len(graph[i])):
                j = graph[i][connection]
                if (i, j) not in done_edges:
                    p += 1
                    done_edges.add((p, i))
                    done_edges.add((j, p))
                    graph[p] = [i, j]  # Adding the periphery to the dicts
                    graph[i][connection] = p  # Modifying the existing connections/darts
                    rotation[p] = 0
                    for o in range(len(graph[j])):
                        if graph[j][o] == i:
                            graph[j][o] = p

        coordinates, darts, _, __ = embed_region_graph(graph, map_size, 0.01, seed)

        weights, fixed_points = dict(), dict()
        for i in graph:
            weights[i] = 1
            fixed_points[i] = 0
        coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, fixed_points, map_size, ratios=(0.1, 0.3, 100), iterations=1000)  # final pass to clean up the embedding

        # find rotations of peripheries
        for p in rotation:
            i = graph[p][0]
            i_dart = darts[i][graph[i].index(p)]
            vector = np.subtract(np.add(coordinates[p], np.multiply(i_dart, map_size)), coordinates[i])
            rotation[p] = 90 + np.angle(vector[0] + vector[1] * 1j, deg=True)

        edges_set, embedding = set(), dict()
        for i in graph:  # edges_set is an undirected graph as a set of undirected edges
            j_angles = []
            for j in graph[i]:
                edges_set |= {(i, j), (j, i)}
                vector = coordinates[j] + np.multiply(darts[i][graph[i].index(j)], map_size) - coordinates[i]
                angle = 90-np.angle(vector[0] + vector[1] * 1j, deg=True)
                j_angles.append([j, angle])

            j_angles.sort(key=lambda x: x[1])
            embedding[i] = [x[0] for x in j_angles]  # Format: v1:[v2,v3], v2:[v1], v3:[v1] clockwise ordering of neighbors at each vertex

        faces, path = list(), list()  # Storage for face paths
        path.append((i, j))
        edges_set -= {(i, j)}

        while len(edges_set) > 0:  # Trace faces
            neighbors = embedding[path[-1][-1]]
            next_node = neighbors[(neighbors.index(path[-1][-2]) + 1) % (len(neighbors))]
            tup = (path[-1][-1], next_node)
            if tup == path[0]:
                faces.append(path)
                path = list()
                for edge in edges_set:
                    path.append(edge)
                    edges_set -= {edge}
                    break  # (Only one iteration)
            else:
                path.append(tup)
                edges_set -= {tup}
        if len(path) != 0:
            faces.append(path)

        potential_thrones = list()
        for face in faces:
            shift = np.subtract(np.divide(map_size, 2), coordinates[face[0][0]])
            total = np.zeros(2)
            for edge in face:
                i = edge[0]
                total = total + (np.add(coordinates[i], shift)) % map_size
            coordinate = (-shift + total / len(face)) % map_size
            potential_thrones.append((int(coordinate[0]), int(coordinate[1])))

        # Assign these as good throne locations
        if self.map.settings.throne_sites > len(potential_thrones):
            return Exception("\033[31m" + "Error: more thrones (%i) than good throne locations (%i)\x1b[0m" % (self.map.settings.throne_sites, len(potential_thrones)))
        if self.map.settings.throne_sites < len(potential_thrones):
            print("\033[31m" + "Warning: less thrones (%i) than good throne locations (%i). Selecting best locations.\x1b[0m" % (self.map.settings.throne_sites, len(potential_thrones)))

            while len(potential_thrones) > self.map.settings.throne_sites:
                min_square_dist = np.inf
                for throne in potential_thrones:
                    square_sum = 0
                    for other_throne in potential_thrones:
                        min_dist = np.inf
                        for neighbour in NEIGHBOURS_FULL:
                            vector = other_throne + neighbour * map_size - throne
                            distance = np.linalg.norm(vector)
                            if distance < min_dist:
                                min_dist = distance
                        square_sum += min_dist ** 4
                    if square_sum < min_square_dist:
                        min_square_dist = square_sum
                        to_remove = throne
                potential_thrones.remove(to_remove)

        t = len(graph) + 1
        for _ in range(self.map.settings.throne_sites):  # Adding the throne to the dicts
            coordinate = rd.choice(potential_thrones)
            potential_thrones.remove(coordinate)
            graph[t] = []
            coordinates[t] = [coordinate[0], coordinate[1]]
            darts[t] = []
            rotation[t] = 0
            t += 1

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

        weights, fixed_points, lloyd_points, count_2_index = dict(), dict(), list(), dict()
        counter = 0
        for index in range(len(province_list)):
            province = province_list[index]
            weights[province.index] = province.size
            if province.fixed:
                fixed_points[province.index] = 0
            else:
                fixed_points[province.index] = 0
                lloyd_points.append(province_list[index].coordinates)
                count_2_index[counter] = index
                counter += 1

        lloyd = LloydRelaxation(np.array(lloyd_points))
        for _ in range(1):
            lloyd.relax()
        lloyd_points = lloyd.get_points()
        for index in range(len(lloyd_points)):
            province_list[count_2_index[index]].coordinates = lloyd_points[index]

        graph, coordinates, darts = make_delaunay_graph(province_list, map_size)
        coordinates, darts = spring_electron_adjustment(graph, coordinates, darts, weights, fixed_points, map_size, ratios=(0.4, 0.4, 50), iterations=3000)

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

    def generate_gates(self,
                       seed: int = None):
        dibber(self, seed)  # Setting random seed

        self.gates, region_plane_dict, region_list = [[] for _ in range(10)], dict(), list()
        for plane in range(1, 10):  # sort the provinces into region-plane buckets and remove invalid candidates
            region_plane_dict[plane] = dict()
            for province in self.map.province_list[plane]:
                if not province.capital_location and not has_terrain(province.terrain_int, 4):
                    if province.parent_region not in region_plane_dict[plane]:  # Add
                        region_plane_dict[plane][province.parent_region] = []
                        if province.parent_region not in region_list:
                            region_list.append(province.parent_region)

                    region_plane_dict[plane][province.parent_region].append(province.index)

        gate = 1
        for region in region_list:  # randomly gate them
            planes = []
            for plane in range(1, 10):
                try:
                    thing = len(region_plane_dict[plane][region])
                except:
                    continue
                planes.append(plane)
            if len(planes) > 1:
                for link in range(2):
                    choice1 = rd.choice(region_plane_dict[1][region])
                    choice2 = rd.choice(region_plane_dict[2][region])
                    region_plane_dict[1][region].remove(choice1)
                    region_plane_dict[2][region].remove(choice2)
                    self.gates[1].append([choice1, gate])
                    self.gates[2].append([choice2, gate])
                    gate += 1

    def plot(self):

        fig, axs = plt.subplots(1 + len(self.map.planes), 1)
        ax_regions = axs[0]
        ax_provinces = axs[1:]

        # Plot regions
        virtual_graph, virtual_coordinates = make_virtual_graph(self.region_graph, self.region_coordinates, self.region_darts, self.map.map_size[1])
        for i in virtual_graph:  # region connections
            x0, y0 = virtual_coordinates[i]
            for j in virtual_graph[i]:
                x1, y1 = virtual_coordinates[j]
                ax_regions.plot([x0, x1], [y0, y1], 'k-')

        for i in self.region_graph:
            x0, y0 = self.region_coordinates[i]
            if i <= len(self.map.settings.nations)+len(self.map.settings.custom_nations):
                colour = 'go'
            elif i <= len(self.region_graph) - self.map.settings.throne_sites:
                colour = 'ro'
            else:
                colour = 'yo'
            ax_regions.plot(x0, y0, colour)
            ax_regions.text(x0, y0, str(i))
        ax_regions.set(xlim=(0, self.map.map_size[1][0]), ylim=(0, self.map.map_size[1][1]))

        # Plot provinces
        for index in range(len(self.map.planes)):
            plane = self.map.planes[index]
            ax = ax_provinces[index]
            virtual_graph, virtual_coordinates = make_virtual_graph(self.graph[plane], self.coordinates[plane], self.darts[plane], self.map.map_size[plane])
            for i in virtual_graph:  # region connections
                x0, y0 = virtual_coordinates[i]
                for j in virtual_graph[i]:
                    x1, y1 = virtual_coordinates[j]
                    ax.plot([x0, x1], [y0, y1], 'k-')

            for i in self.graph[plane]:
                x0, y0 = self.coordinates[plane][i]
                ax.plot(x0, y0, 'ro')
                ax.text(x0, y0, str(i))
            ax.set(xlim=(0, self.map.map_size[plane][0]), ylim=(0, self.map.map_size[plane][1]))



