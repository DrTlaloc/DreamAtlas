# Imports all the DreamAtlas functionality and dependencies
from DreamAtlas import *


@njit(parallel=True)
def _jump_flood_algorithm(matrix: np.array,
                          seed_array: np.array,
                          step_size: int,
                          closest_distance_matrix: np.array,
                          weight_array: np.array = None,
                          shape_array: np.array = None,
                          hwrap: bool = True,
                          vwrap: bool = True):
    if weight_array is None:
        weight_array = np.zeros(len(seed_array))
        for i in range(len(seed_array)):
            weight_array[i] = 1

    if shape_array is None:
        shape_array = np.zeros(len(seed_array))
        for i in range(len(seed_array)):
            shape_array[i] = 2

    size_shape_factor = np.zeros(len(seed_array), dtype=np.float64)
    for i in range(len(seed_array)):
        size_shape_factor[i] = np.power(weight_array[i], 1 / shape_array[i])

    end = False
    size = matrix.shape

    ping_matrix = matrix
    pong_matrix = matrix

    while True:
        step_size = int(0.5 + step_size / 2)
        neighbours = np.array([[step_size, -step_size], [step_size, 0], [step_size, step_size], [0, step_size],
                               [-step_size, step_size], [0, -step_size], [-step_size, -step_size], [-step_size, 0]],
                              dtype=np.int32)

        for x in prange(size[0]):
            for y in range(size[1]):
                p = ping_matrix[x, y]
                for n in range(len(neighbours)):
                    qx = x + neighbours[n][0]
                    qy = y + neighbours[n][1]
                    ix = qx % size[0]
                    iy = qy % size[1]
                    q = ping_matrix[ix, iy]

                    # Main logic of the Jump Flood Algorithm
                    if p == q:
                        pass
                    elif p == 0 and q != 0:
                        closest_distance_matrix[x, y] = np.linalg.norm(
                            np.multiply(size_shape_factor[q], np.array([x - qx, y - qy]) +
                                        np.array([ix - seed_array[q, 0], iy - seed_array[q, 1]])), ord=shape_array[q])

                        pong_matrix[x, y] = q
                    else:
                        q_dist = np.linalg.norm(
                            np.multiply(size_shape_factor[q], np.array([x - qx, y - qy]) +
                                        np.array([ix - seed_array[q, 0], iy - seed_array[q, 1]])), ord=shape_array[q])
                        if closest_distance_matrix[x, y] > q_dist:
                            closest_distance_matrix[x, y] = q_dist
                            pong_matrix[x, y] = q

        ping_matrix = pong_matrix

        if end and step_size == 1:  # Breaking the while loop
            break
        if step_size == 1:  # Does a final pass
            step_size = 64
            end = True

    return ping_matrix


def find_pixel_ownership(coordinates_dict: dict,
                         map_size: list[float, float],
                         weights: dict,
                         shapes: dict,
                         hwrap: bool = True,
                         vwrap: bool = True,
                         scale_down: int = 8):
    # Runs a jump flood algorithm on a scaled down version of the map, then scales up and redoes the algorithm more
    # finely. This speeds up runtime significantly. The main function of the JFA is run in Numba, which speeds up the
    # code and allows it to be run in parallel on CPU or GPU.

    small_x_size = int(map_size[0] / scale_down)
    small_y_size = int(map_size[1] / scale_down)
    small_matrix = np.zeros((small_x_size, small_y_size), dtype=np.int32)
    dict_size = max(coordinates_dict) + 1
    small_seed_array = np.empty((dict_size, 2), dtype=np.int32)
    weight_array = np.ones(dict_size, dtype=np.float64)
    shape_array = np.ones(dict_size, dtype=np.float64)
    for point in coordinates_dict:
        x, y = coordinates_dict[point]
        x_small = int((x / scale_down) % small_x_size)
        y_small = int((y / scale_down) % small_y_size)
        small_seed_array[point] = [x_small, y_small]
        small_matrix[x_small, y_small] = point
        weight_array[point] = weights[point]
        shape_array[point] = shapes[point]

    small_distance_matrix = np.multiply(1000, np.ones((small_x_size, small_y_size), dtype=np.float64))
    small_output_matrix = _jump_flood_algorithm(small_matrix,
                                                small_seed_array,
                                                step_size=2 ** (int(2 + np.log(max(map_size) / scale_down))),
                                                closest_distance_matrix=small_distance_matrix,
                                                weight_array=weight_array,
                                                shape_array=shape_array)

    # Scale the matrix back up and run a JFA again to refine
    zoom = map_size[0] / small_output_matrix.shape[0]
    final_matrix = sc.ndimage.zoom(small_output_matrix, zoom=zoom, order=0)
    final_matrix = final_matrix[:map_size[0], :map_size[1]]
    final_matrix = final_matrix.astype(np.int32)
    final_distance_matrix = np.multiply(2000, np.ones((final_matrix.shape[0], final_matrix.shape[1]), dtype=np.float64))

    final_seed_array = np.empty((dict_size, 2), dtype=np.int32)
    for point in coordinates_dict:
        x, y = coordinates_dict[point]
        x_final = int((map_size[0] + x) % map_size[0])
        y_final = int((map_size[1] + y) % map_size[1])
        final_seed_array[point] = [x_final, y_final]
        final_matrix[x_final, y_final] = point

    step_size = 2 ** (int(2 + np.log(max(map_size))))

    return _jump_flood_algorithm(final_matrix, final_seed_array, step_size=step_size,
                                 closest_distance_matrix=final_distance_matrix,
                                 weight_array=weight_array,
                                 shape_array=shape_array)


# def pb_pixel_allocation(pixel_matrix):
#
#     pb_combined = np.vstack(_numba_pb_allocation(pixel_matrix))
#     pb_list = []
#     for entry in pb_combined:
#         if entry[2] != 0:
#             pb_list.append(entry)
#
#     return pb_list
#
#
# @njit(parallel=True)
# def _numba_pb_allocation(pixel_matrix):
#     x_size, y_size = pixel_matrix.shape
#     split_pb_list = np.zeros((y_size, x_size, 4), dtype=np.int32)
#
#     for y in prange(y_size):
#         pb_length = 0
#         first_prov_index = pixel_matrix[0, y]
#         x1 = 0
#         for x2 in range(x_size):
#             current_prov_index = pixel_matrix[x2, y]
#             if current_prov_index != first_prov_index:  # If it's a new province id, append the last pb string and start a new one
#                 split_pb_list[y, x1] = [y, x1, pb_length, first_prov_index]
#                 first_prov_index = current_prov_index
#                 x1 = x2
#                 pb_length = 1
#             else:  # If this is the same prov just extend the length and continue
#                 pb_length += 1
#
#     return split_pb_list

def pb_pixel_allocation(pixel_matrix):
    pixel_ownership_list = []
    x_size, y_size = pixel_matrix.shape
    for y in range(y_size):
        pb_length = 1
        first_prov_index = 0
        first_x = 0
        first_y = y
        for x in range(x_size):
            current_prov_index = pixel_matrix[x, y]
            if current_prov_index == first_prov_index:  # If this is the same prov just extend the length and continue
                pb_length += 1
            elif first_prov_index == 0:  # If we're still on the first pb, assign it properly and carry on
                first_prov_index = current_prov_index
            else:  # If it's a new province id, append the last pb string and start a new one
                pixel_ownership_list.append([first_x, first_y, pb_length, first_prov_index])
                first_prov_index = current_prov_index
                first_x = x
                first_y = y
                pb_length = 1

    return pixel_ownership_list
