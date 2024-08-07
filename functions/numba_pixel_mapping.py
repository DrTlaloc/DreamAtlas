# Imports all the DreamAtlas functionality and dependencies
from DreamAtlas import *


@njit(parallel=True)
def _jump_flood_algorithm(pixel_matrix: np.array,
                          seed_array: np.array,
                          step_size: int,
                          weight_array: np.array,
                          shape_array: np.array,
                          distance_matrix: np.array,
                          vector_matrix: np.array,
                          hwrap: bool = True,
                          vwrap: bool = True):

    shape_x, shape_y = np.shape(pixel_matrix)

    size_shape_factor = np.full(len(seed_array), np.inf, dtype=np.float64)
    for i in range(len(seed_array)):
        size_shape_factor[i] = np.power(weight_array[i], 1 / shape_array[i])

    end = False
    ping_matrix = pixel_matrix
    pong_matrix = pixel_matrix
    ping_distance_matrix = distance_matrix
    pong_distance_matrix = distance_matrix
    ping_vector_matrix = vector_matrix
    pong_vector_matrix = vector_matrix
    while True:
        step_size = int(0.5 + step_size / 2)
        neighbours = np.array([[step_size, -step_size], [step_size, 0], [step_size, step_size], [0, step_size],
                               [-step_size, step_size], [0, -step_size], [-step_size, -step_size], [-step_size, 0]],
                              dtype=np.int32)

        for x in prange(shape_x):
            for y in range(shape_y):
                p = ping_matrix[x, y]
                for n in range(len(neighbours)):
                    neighbour = neighbours[n]
                    qx = x + neighbour[0]  # Finds the virtual pixel location (can be outside the matrix)
                    qy = y + neighbour[1]

                    if not hwrap:  # Ensuring the wraparound is respected, if there is no wrapping do not use virtual
                        qx %= shape_x
                    if not vwrap:
                        qy %= shape_y

                    ix = qx % shape_x  # Finds the actual real pixel location (inside the matrix)
                    iy = qy % shape_y
                    q = ping_matrix[ix, iy]

                    # Main logic of the Jump Flood Algorithm (if the pixels are identical or q has no info go to next)
                    if p == q or q == 0:
                        continue
                    q_vector = np.subtract(ping_vector_matrix[ix, iy], neighbour)
                    q_dist = np.linalg.norm(np.multiply(size_shape_factor[q], q_vector), ord=shape_array[q])
                    if p == 0:  # if our pixel is empty, populate it with q
                        pong_distance_matrix[x, y] = q_dist
                        pong_vector_matrix[x, y] = q_vector
                        pong_matrix[x, y] = q
                    else:  # if our pixel is not empty, see if q is closer than p and if so populate it with q
                        if ping_distance_matrix[x, y] > q_dist:
                            pong_distance_matrix[x, y] = q_dist
                            pong_vector_matrix[x, y] = q_vector
                            pong_matrix[x, y] = q

        ping_matrix = pong_matrix
        ping_distance_matrix = pong_distance_matrix
        ping_vector_matrix = pong_vector_matrix

        if end and step_size == 1:  # Breaking the while loop
            break
        if step_size == 1:  # Does a final pass
            step_size = 16
            end = True

    return ping_matrix, ping_distance_matrix, ping_vector_matrix


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
    shape_array = np.full(dict_size, 2, dtype=np.float64)
    s_distance_matrix = np.full((small_x_size, small_y_size), np.inf, dtype=np.float64)
    s_vector_matrix = np.zeros((small_x_size, small_y_size, 2), dtype=np.int32)
    for point in coordinates_dict:
        x, y = coordinates_dict[point]
        x_small = int((x / scale_down) % small_x_size)
        y_small = int((y / scale_down) % small_y_size)
        small_seed_array[point] = [x_small, y_small]
        small_matrix[x_small, y_small] = point
        s_distance_matrix[x_small, y_small] = 0
        weight_array[point] = weights[point]
        shape_array[point] = shapes[point]

    small_output_matrix, small_distance_matrix, small_vector_matrix = _jump_flood_algorithm(small_matrix,
                                                                                            small_seed_array,
                                                                                            step_size=2 ** (int(1 + np.log(max(map_size) / scale_down))),
                                                                                            weight_array=weight_array,
                                                                                            shape_array=shape_array,
                                                                                            distance_matrix=s_distance_matrix,
                                                                                            vector_matrix=s_vector_matrix,
                                                                                            hwrap=hwrap,
                                                                                            vwrap=vwrap)

    # Scale the matrix back up and run a JFA again to refine
    zoom = map_size[0] / small_output_matrix.shape[0]
    final_matrix = sc.ndimage.zoom(small_output_matrix, zoom=zoom, order=0, output=np.int32)[:map_size[0], :map_size[1]]
    final_distance_matrix = np.multiply(small_distance_matrix, scale_down)
    final_distance_matrix = sc.ndimage.zoom(final_distance_matrix, zoom=zoom, order=0, output=np.float64)[:map_size[0], :map_size[1]]
    final_vector_matrix = np.multiply(small_vector_matrix, scale_down)
    final_vector_matrix = sc.ndimage.zoom(final_vector_matrix, zoom=[zoom, zoom, 1], order=0, output=np.int32)[:map_size[0], :map_size[1]]

    final_seed_array = np.empty((dict_size, 2), dtype=np.int32)
    for point in coordinates_dict:
        x, y = coordinates_dict[point]
        x_final = int((map_size[0] + x) % map_size[0])
        y_final = int((map_size[1] + y) % map_size[1])
        final_seed_array[point] = [x_final, y_final]
        final_matrix[x_final, y_final] = point

    final_matrix, _, __ = _jump_flood_algorithm(final_matrix, final_seed_array,
                                                step_size=2 ** (int(np.log(max(map_size)))),
                                                weight_array=weight_array,
                                                shape_array=shape_array,
                                                distance_matrix=final_distance_matrix,
                                                vector_matrix=final_vector_matrix,
                                                hwrap=hwrap,
                                                vwrap=vwrap)

    return final_matrix


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
