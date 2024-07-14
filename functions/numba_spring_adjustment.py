from DreamAtlas import *


@njit(parallel=True)
def _numba_spring_electron_adjustment(key_list: np.array,
                                      graph: np.array,
                                      coordinates: np.array,
                                      darts: np.array,
                                      weight_array: np.array,
                                      map_size: list[float, float],
                                      ratios: tuple[float, float],
                                      iterations: int):
    dict_size = len(key_list)
    damping_ratio, spring_coefficient = ratios
    map_size_array = np.asarray(map_size, dtype=np.float64)

    neighbours = np.array([[0, 0], [map_size[0], -map_size[1]], [map_size[0], 0], [map_size[0], map_size[1]],
                           [0, map_size[1]], [-map_size[0], map_size[1]], [0, -map_size[1]],
                           [-map_size[0], -map_size[1]], [-map_size[0], 0]])

    electron_vector_matrix = np.zeros(shape=(dict_size, dict_size, 2))
    for i in prange(dict_size):
        for j in range(dict_size):
            if i == j:
                electron_vector_matrix[i, j] = [0, 0]
            else:
                closest_distance = np.Inf
                for n in neighbours:
                    virtual_vector = np.asarray(coordinates[i] - coordinates[j] + n, dtype=np.float64)
                    virtual_distance = np.linalg.norm(virtual_vector)
                    if virtual_distance < closest_distance:
                        closest_distance = virtual_distance
                        closest_vector = virtual_vector

                electron_vector = closest_vector / (0.1 + closest_distance ** 2)
                electron_vector_matrix[i, j] = electron_vector

    velocity = np.zeros((dict_size, 2))
    equilibrium = False
    for _ in range(iterations):
        for i in prange(dict_size):
            electron_force = np.zeros(2)
            spring_force = np.zeros(2)

            for j in range(dict_size):  # Calculate repulsion (to the nearest version of each node)
                electron_force = electron_force + electron_vector_matrix[i, j]

            for j in range(dict_size):  # Calculates spring force to connections
                if graph[i, j] == 1:
                    spring_vector = coordinates[j] + darts[i, j] * map_size_array - coordinates[i]
                    unit_vector = spring_vector / (0.001 + np.linalg.norm(spring_vector))
                    spring_force = spring_force + spring_coefficient * (spring_vector - 50 * unit_vector * weight_array[j])

            velocity[i] = damping_ratio * (velocity[i] + electron_force + spring_force)

        for i in range(dict_size):  # Check if non-fixed particles are within tolerance
            if np.linalg.norm(velocity[i]) > 0.01:
                break
            if i == dict_size - 1:
                equilibrium = True

        for i in range(dict_size):  # Update the position
            coordinates[i] = coordinates[i] + velocity[i]

            if not ((0 <= coordinates[i, 0] < map_size_array[0]) and (0 <= coordinates[i, 1] < map_size_array[1])):  # Checking torus constraints
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


def spring_electron_adjustment(graph: dict,
                               coordinates: dict,
                               darts: dict,
                               weights: dict,
                               map_size: tuple[int, int],
                               ratios: tuple[float, float],
                               iterations: int):

    key_list = np.zeros(len(graph), dtype=int)
    graph_array = np.zeros((len(graph), len(graph)), dtype=int)
    coordinates_array = np.zeros((len(graph), 2), dtype=int)
    darts_array = np.zeros((len(graph), len(graph), 2))
    weight_array = np.ones(len(graph))

    index = 0
    for i in graph:
        key_list[index] = i
        coordinates_array[index] = coordinates[i]
        weight_array[index] = weights[i]

        index2 = 0
        for j in graph:
            if j in graph[i]:
                ji = graph[i].index(j)
                graph_array[index, index2] = 1
                darts_array[index, index2] = darts[i][ji]
            else:
                graph_array[index, index2] = 0
                darts_array[index, index2] = [np.NaN, np.NaN]
            index2 += 1
        index += 1

    _coordinates, _darts = _numba_spring_electron_adjustment(key_list, graph_array, coordinates_array, darts_array, weight_array, [map_size[0], map_size[1]], ratios, iterations)
    graph_output = {}
    coordinates_output = {}
    darts_output = {}
    for i in range(len(key_list)):
        coordinates_output[key_list[i]] = _coordinates[i].tolist()

        graph_output[key_list[i]] = []
        darts_output[key_list[i]] = []
        for j in range(len(key_list)):
            if graph_array[i, j] == 1:
                graph_output[key_list[i]].append(key_list[j])
                darts_output[key_list[i]].append(_darts[i, j].tolist())

    return graph_output, coordinates_output, darts_output
