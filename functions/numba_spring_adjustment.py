import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True)
def _numba_spring_electron_adjustment(key_list: np.array,
                                      graph: np.array,
                                      coordinates: np.array,
                                      darts: np.array,
                                      weight_array: np.array,
                                      map_size: np.array,
                                      ratios: np.array,
                                      connections: np.array,
                                      iterations: int):

    dict_size = len(key_list)
    damping_ratio, spring_coefficient, base_length = ratios

    net_velocity = np.zeros((dict_size, 2), dtype=np.float32)
    for _ in range(iterations):
        net_spring_force = np.zeros((dict_size, 2), dtype=np.float32)
        for i, j in connections:
            length = base_length * (weight_array[i] + weight_array[j])
            vector = coordinates[j] + darts[i, j] * map_size - coordinates[i]
            unit_vector = vector / (0.0000001 + np.linalg.norm(vector))

            spring_force = vector - unit_vector * length
            net_spring_force[i] += spring_force

        net_velocity = damping_ratio * (net_velocity + spring_coefficient * net_spring_force)

        equilibrium = 1
        for c in range(dict_size):  # Check if particles are within tolerance
            if np.linalg.norm(net_velocity[c]) > 0.0001:
                equilibrium = 0
                break

        coordinates += net_velocity
        for a in range(dict_size):  # Update the position
            for axis in range(2):
                if not (0 <= coordinates[a, axis] < map_size[axis]):
                    dart_change = -np.sign(coordinates[a, axis])
                    coordinates[a, axis] = coordinates[a, axis] % map_size[axis]

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
                               map_size: np.array,
                               ratios: np.array,
                               iterations: int):

    key_list = np.zeros(len(graph), dtype=np.uint32)
    graph_array = np.zeros((len(graph), len(graph)), dtype=np.bool_)
    coordinates_array = np.zeros((len(graph), 2), dtype=np.float32)
    darts_array = np.zeros((len(graph), len(graph), 2), dtype=np.int8)
    weight_array = np.ones(len(graph), dtype=np.float32)
    map_size = map_size.astype(dtype=np.float32)
    ratios = ratios.astype(dtype=np.float32)

    index = 0
    for i in graph:
        key_list[index] = i
        coordinates_array[index] = coordinates[i]
        index2 = 0
        for j in graph:
            if j in graph[i]:
                graph_array[index, index2] = 1
                darts_array[index, index2] = darts[i][graph[i].index(j)]
            index2 += 1
        index += 1

    index = 0
    for i in graph:
        weight_array[index] = weights[i]
        index += 1

    connections = np.transpose(np.nonzero(graph_array))
    _coordinates, _darts = _numba_spring_electron_adjustment(key_list, graph_array, coordinates_array, darts_array, weight_array, map_size, ratios, connections, iterations)
    coordinates_output, darts_output = dict(), dict()
    for i in range(len(key_list)):
        coordinates_output[key_list[i]] = _coordinates[i].astype(np.int32).tolist()
        darts_output[key_list[i]] = list()
        for j in range(len(key_list)):
            if graph_array[i, j] == 1:
                darts_output[key_list[i]].append(_darts[i, j].astype(np.int8).tolist())

    return coordinates_output, darts_output
