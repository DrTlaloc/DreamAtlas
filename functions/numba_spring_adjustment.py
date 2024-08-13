from DreamAtlas import *


@njit(parallel=True)
def _numba_spring_electron_adjustment(key_list: np.array,
                                      graph: np.array,
                                      coordinates: np.array,
                                      darts: np.array,
                                      weight_array: np.array,
                                      fixed_array: np.array,
                                      map_size: list[float, float],
                                      ratios: tuple[float, float, float],
                                      iterations: int):
    dict_size = len(key_list)
    damping_ratio, spring_coefficient, electron_coefficient = ratios
    map_size_array = np.asarray(map_size, dtype=np.float64)
    neighbours = np.array([[0, 0], [map_size[0], -map_size[1]], [map_size[0], 0], [map_size[0], map_size[1]],
                           [0, map_size[1]], [-map_size[0], map_size[1]], [0, -map_size[1]],
                           [-map_size[0], -map_size[1]], [-map_size[0], 0]], dtype=np.float64)
    neighbours_size = len(neighbours)

    velocity, electron_force, spring_force = np.zeros((dict_size, 2), dtype=np.float64), np.zeros((dict_size, 2), dtype=np.float64), np.zeros((dict_size, 2), dtype=np.float64)

    equilibrium = False
    for _ in range(iterations):
        for i in prange(dict_size):
            electron_force[i], spring_force[i] = np.zeros(2), np.zeros(2)
            if fixed_array[i] == 1:
                velocity[i] = np.zeros(2)
            else:
                for j in range(dict_size):  # Calculate repulsion (to the nearest version of each node)
                    if i != j:
                        virtual_vectors = np.zeros((neighbours_size, 2), dtype=np.float64)
                        virtual_distances = np.zeros(neighbours_size, dtype=np.float64)
                        for n in range(neighbours_size):
                            virtual_vectors[n] = coordinates[i] - coordinates[j] - neighbours[n]
                            virtual_distances[n] = np.linalg.norm(virtual_vectors[n])
                        min_dist = np.min(virtual_distances)
                        electron_force[i] = electron_force[i] + electron_coefficient * weight_array[j] * virtual_vectors[np.where(virtual_distances == min_dist)] / (0.1 + min_dist ** 2)

                    if graph[i, j] == 1:
                        spring_force[i] = spring_force[i] + spring_coefficient * (coordinates[j] + darts[i, j] * map_size_array - coordinates[i])

                velocity[i] = damping_ratio * (velocity[i] + electron_force[i] + spring_force[i])

        for c in range(dict_size):  # Check if non-fixed particles are within tolerance
            if np.linalg.norm(velocity[c]) > 0.0001:
                break
            if c == dict_size - 1:
                equilibrium = True

        for a in range(dict_size):  # Update the position
            coordinates[a] = coordinates[a] + velocity[a]

            if not ((0 <= coordinates[a, 0] < map_size_array[0]) and (0 <= coordinates[a, 1] < map_size_array[1])):  # Checking torus constraints
                for axis in range(2):
                    if not (0 <= coordinates[a, axis] < map_size_array[axis]):
                        dart_change = -np.sign(coordinates[a, axis])
                        coordinates[a, axis] = int(coordinates[a, axis] % map_size_array[axis])

                        for b in range(dict_size):  # Iterating over all of this vertex's connections
                            if graph[a, b]:
                                new_value = darts[a, b, axis] + dart_change
                                if new_value < -1:
                                    new_value = 1
                                if new_value > 1:
                                    new_value = -1

                                darts[a, b, axis] = int(new_value)  # Setting the dart for this vertex
                                darts[b, a, axis] = int(-new_value)  # Setting the dart for other vertex
        if equilibrium:
            break
    return coordinates, darts


def spring_electron_adjustment(graph: dict,
                               coordinates: dict,
                               darts: dict,
                               weights: dict,
                               fixed_points: list,
                               map_size: tuple[int, int],
                               ratios: tuple[float, float, float],
                               iterations: int):

    key_list = np.zeros(len(graph), dtype=int)
    graph_array = np.zeros((len(graph), len(graph)), dtype=int)
    coordinates_array = np.zeros((len(graph), 2), dtype=np.float64)
    darts_array = np.zeros((len(graph), len(graph), 2))
    weight_array = np.ones(len(graph))
    fixed_array = np.zeros(len(graph), dtype=int)

    index = 0
    for i in graph:
        key_list[index] = i
        coordinates_array[index] = coordinates[i]
        weight_array[index] = weights[i]
        if i in fixed_points:
            fixed_array[index] = 1

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

    _coordinates, _darts = _numba_spring_electron_adjustment(key_list, graph_array, coordinates_array, darts_array, weight_array, fixed_array, [map_size[0], map_size[1]], ratios, iterations)
    coordinates_output = {}
    darts_output = {}
    for i in range(len(key_list)):
        coordinates_output[key_list[i]] = _coordinates[i].astype(np.int32).tolist()
        darts_output[key_list[i]] = []
        for j in range(len(key_list)):
            if graph_array[i, j] == 1:
                darts_output[key_list[i]].append(_darts[i, j].tolist())

    return coordinates_output, darts_output
