from DreamAtlas import *


def embed_region_graph(graph: dict,
                       map_size: tuple[int, int],
                       scale_down: float,
                       seed: int):

    graph_range = range(1, 1 + len(graph))

    # Set the graph size to embed (smaller is faster)
    x_size = int(scale_down * map_size[0])
    y_size = int(scale_down * map_size[1])
    connections = [[1, 0], [0, 1], [0, -1], [-1, 0]]

    # Make the H graph
    target_graph = dict()
    for x in range(x_size):
        for y in range(y_size):
            target_graph[(int(x / scale_down), int(y / scale_down))] = list()
            for connection in connections:
                x_coord = int(((x + connection[0]) % x_size) / scale_down)
                y_coord = int(((y + connection[1]) % y_size) / scale_down)
                target_graph[(int(x / scale_down), int(y / scale_down))].append((x_coord, y_coord))

    target_graph = ntx.Graph(incoming_graph_data=target_graph)

    initial_embedding, worked = mnm.find_embedding(ntx.Graph(incoming_graph_data=graph), target_graph, return_overlap=True, random_seed=seed, verbose=1)

    # Form the subgraph of the target graph
    subgraph_nodes, node_2_index = list(), dict()
    for i in graph_range:
        for node in initial_embedding[i]:
            node_2_index[node] = i
            subgraph_nodes.append(node)
    subgraph = target_graph.subgraph(subgraph_nodes)

    # Build the graph for attractor adjustment
    attractor_graph, attractor_coordinates, attractor_darts, done_edges = dict(), dict(), dict(), set()
    for i in graph_range:
        for node in initial_embedding[i]:  # Loop over all the embedded nodes
            attractor_graph[node] = []
            attractor_coordinates[node] = [node[0], node[1]]
            attractor_darts[node] = []

            for edge in ntx.edges(subgraph, node):  # Add the connected nodes and darts
                j = node_2_index[edge[1]]
                if j == i or j in graph[i]:
                    dart = [0, 0]
                    for axis in range(2):
                        if abs(edge[0][axis] - edge[1][axis]) > 1 / scale_down:
                            dart[axis] = np.sign(edge[0][axis] - edge[1][axis])
                    attractor_graph[node].append(edge[1])
                    attractor_darts[node].append(dart)

    attractor_coordinates, attractor_darts = attractor_adjustment(attractor_graph, attractor_coordinates, attractor_darts, node_2_index, map_size, damping_ratio=0.5, iterations=100)

    coordinates, darts, done_edges = dict(), dict(), set()
    for i in graph:  # Merge the alike vertices of the graph
        coordinate_sum = 0
        coordinates_offset = np.subtract(np.divide(map_size, 2), attractor_coordinates[initial_embedding[i][0]])
        for node in initial_embedding[i]:  # Loop over all the nodes for this vertex
            coordinate_sum += np.mod(np.add(coordinates_offset, attractor_coordinates[node]), map_size)
        coordinates[i] = np.mod(np.subtract(np.divide(coordinate_sum, len(initial_embedding[i])), coordinates_offset), map_size)

    for i in graph:  # Make final darts
        darts[i] = []
        for j in graph[i]:
            dart_candidates = []
            for node1 in initial_embedding[i]:
                for node2 in initial_embedding[j]:
                    if node2 in attractor_graph[node1]:
                        dart = attractor_darts[node1][attractor_graph[node1].index(node2)]
                        dart_candidates.append(dart)
            darts[i].append(dart)

    return coordinates, darts, attractor_coordinates, node_2_index


@njit(parallel=True)
def _numba_attractor_adjustment(key_list: np.array,
                                graph: np.array,
                                coordinates: np.array,
                                darts: np.array,
                                attractor_array: np.array,
                                damping_ratio: float,
                                map_size: tuple[int, int],
                                iterations: int):
    dict_size = len(key_list)
    map_size_array = np.asarray(map_size, dtype=np.float64)
    velocity = np.zeros((dict_size, 2))

    equilibrium = False
    for _ in range(iterations):

        for i in prange(dict_size):
            attractor_force = np.zeros(2)
            for j in range(dict_size):
                if attractor_array[i, j] == 1:
                    attractor_force = attractor_force + np.asarray(coordinates[j] + darts[i, j] * map_size_array - coordinates[i], dtype=np.float64)
            velocity[i] = damping_ratio * (velocity[i] + attractor_force)

        for i in range(dict_size):  # Check if non-fixed particles are within tolerance
            if np.linalg.norm(velocity[i]) > 0.001:
                break
            if i == dict_size - 1:
                equilibrium = True

        for i in range(dict_size):  # Update the position
            coordinates[i] = coordinates[i] + velocity[i]

            for axis in range(2):
                if not (0 <= coordinates[i, axis] < map_size_array[axis]):
                    dart_change = -np.sign(coordinates[i, axis])
                    coordinates[i, axis] = int(coordinates[i, axis] % map_size_array[axis])

                    for j in range(dict_size):  # Iterating over all of this vertex's connections
                        if graph[i, j]:
                            new_value = darts[i, j, axis] + dart_change
                            if new_value < -1:
                                new_value = 1
                            if new_value > 1:
                                new_value = -1

                            darts[i, j, axis] = int(new_value)  # Setting the dart for this vertex
                            darts[j, i, axis] = int(-new_value)  # Setting the dart for other vertex
        if equilibrium:
            break
    return coordinates, darts


def attractor_adjustment(graph: dict,
                         coordinates: dict,
                         darts: dict,
                         node_2_index: dict,
                         map_size: tuple[int, int],
                         damping_ratio: float,
                         iterations: int):

    key_list = np.zeros(len(graph), dtype=int)
    graph_array = np.zeros((len(graph), len(graph)), dtype=int)
    coordinates_array = np.zeros((len(graph), 2), dtype=int)
    darts_array = np.zeros((len(graph), len(graph), 2), dtype=int)
    attractor_array = np.zeros((len(graph), len(graph)), dtype=int)

    ref_2_node, node_2_ref = dict(), dict()
    index = 0
    for node in node_2_index:
        ref_2_node[index] = node
        node_2_ref[node] = index
        index += 1

    index = 0
    for i in graph:
        key_list[index] = node_2_ref[i]
        coordinates_array[index] = coordinates[i]

        index2 = 0
        for j in graph:
            if j in graph[i]:
                ji = graph[i].index(j)
                graph_array[index, index2] = 1
                darts_array[index, index2] = darts[i][ji]
                if node_2_index[j] == node_2_index[i]:
                    attractor_array[index, index2] = 1
            else:
                graph_array[index, index2] = 0
                darts_array[index, index2] = [0, 0]
            index2 += 1
        index += 1

    _coordinates, _darts = _numba_attractor_adjustment(key_list, graph_array, coordinates_array, darts_array, attractor_array, damping_ratio, map_size, iterations)
    coordinates_output, darts_output = dict(), dict()

    for i in range(len(key_list)):
        node = ref_2_node[key_list[i]]
        coordinates_output[node] = _coordinates[i].tolist()
        darts_output[node] = [None] * len(graph[node])
        for j in range(len(key_list)):
            if graph_array[i, j]:
                darts_output[node][graph[node].index(ref_2_node[key_list[j]])] = _darts[i, j].tolist()

    return coordinates_output, darts_output

