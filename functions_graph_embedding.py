from . import *


def minor_graph_embedding(source_graph, map_size, scale_down, seed=None):
    graph_range = range(len(source_graph))

    # Set the graph size to embed (smaller is faster)
    x_size = int(scale_down * map_size[0])
    y_size = int(scale_down * map_size[1])
    connections = [[1, 0], [0, 1], [0, -1], [-1, 0]]

    # Make the H graph
    target_graph = {}
    for x in range(x_size):
        for y in range(y_size):
            target_graph[(x / scale_down, y / scale_down)] = []
            # add each 4 connections including the wraparound
            for connection in connections:
                x_coord = x + connection[0]
                if x_coord < 0:
                    x_coord = x_size - 1
                elif x_coord >= x_size:
                    x_coord = 0

                y_coord = y + connection[1]
                if y_coord < 0:
                    y_coord = y_size - 1
                elif y_coord >= y_size:
                    y_coord = 0

                target_graph[(x / scale_down, y / scale_down)].append((x_coord / scale_down, y_coord / scale_down))

    target_graph = ntx.Graph(incoming_graph_data=target_graph)

    initial_embedding, worked = mnm.find_embedding(source_graph, target_graph, return_overlap=True)

    # Form the subgraph of the target graph
    subgraph_nodes = []
    embedded_coordinates = {}
    for vertex in graph_range:
        embedded_coordinates[vertex + 1] = []
        for sub_vertex in initial_embedding[vertex + 1]:
            subgraph_nodes.append(sub_vertex)
            embedded_coordinates[vertex + 1].append([sub_vertex[0], sub_vertex[1]])

    subgraph = target_graph.subgraph(subgraph_nodes)

    # Go through the vertices and merge them all; if crossovers found, do the merge coordinates average opposite
    final_graph = {}
    final_coordinates = {}
    final_darts = {}

    wrap_list = [[], []]
    original_connection = {}
    for vertex in graph_range:
        graph = []
        darts = []
        coords = [[], []]
        internal_size = 0
        wrap = [False, False]

        sub_vertices = initial_embedding[vertex + 1]
        for node in subgraph.nodes:
            if node in sub_vertices:
                internal_size += 1
                coords[0].append(node[0])
                coords[1].append(node[1])

                for edge in ntx.edges(subgraph, node):

                    # Determine the dart
                    dart = [0, 0]
                    x1, y1 = edge[0]
                    x2, y2 = edge[1]

                    if (x1 == 0) and (x2 == map_size[0] - 1 / scale_down):
                        dart[0] = -1
                    elif (x2 == 0) and (x1 == map_size[0] - 1 / scale_down):
                        dart[0] = 1
                    if (y1 == 0) and (y2 == map_size[1] - 1 / scale_down):
                        dart[1] = -1
                    elif (y2 == 0) and (y1 == map_size[1] - 1 / scale_down):
                        dart[1] = 1

                    # Determine if its another vertex
                    for other_node in subgraph.nodes:
                        if other_node == edge[1]:
                            for other_vertex in graph_range:
                                if (other_vertex + 1) not in graph:
                                    if other_node in initial_embedding[other_vertex + 1]:
                                        if other_vertex+1 in source_graph[vertex+1]:  # connections to other vertices get added
                                            graph.append(other_vertex + 1)
                                            darts.append(dart)
                                            original_connection[(vertex+1, other_vertex+1)] = edge
                                        elif other_vertex == vertex:  # connections to this vertex get merged
                                            if dart[0] != 0:
                                                wrap[0] = True
                                            if dart[1] != 0:
                                                wrap[1] = True

        # if a crossover in the internal zone, do the shift to work out centroid, then go back\
        avr = [[], []]
        for axis in range(2):
            avr[axis] = np.sum(coords[axis]) / internal_size
            if wrap[axis]:
                for index in range(len(coords[axis])):
                    coords[axis][index] -= map_size[axis] / 2
                    coords[axis][index] = coords[axis][index] % map_size[axis]
                avr[axis] = (map_size[axis] / 2 + (np.sum(coords[axis]) / internal_size)) % map_size[axis]
                wrap_list[axis].append(vertex + 1)

        final_graph[vertex + 1] = graph
        final_coordinates[vertex + 1] = [avr[0], avr[1]]
        final_darts[vertex + 1] = darts

    # When there is a crossover determine dart changes
    for vertex in graph_range:
        this_coords = final_coordinates[vertex + 1]
        for axis in range(2):
            if vertex + 1 in wrap_list[axis]:
                for index in range(len(final_graph[vertex + 1])):
                    other_vertex = final_graph[vertex + 1][index]
                    other_coords = final_coordinates[other_vertex]
                    original_edge = original_connection[(vertex+1, other_vertex)]
                    original_dart = final_darts[vertex+1][index]

                    for thing in range(len(final_graph[other_vertex])):
                        if final_graph[other_vertex][thing] == vertex + 1:
                            index2 = thing
                            break

                    # this section is not right, pink and green for sure

                    if other_vertex not in wrap_list[axis]:
                        if abs(this_coords[axis] - other_coords[axis]) < map_size[axis] / 2:
                            final_darts[vertex + 1][index][axis] = 0
                            final_darts[other_vertex][index2][axis] = 0
                        else:
                            if this_coords[axis] > map_size[axis] / 2:
                                final_darts[vertex + 1][index][axis] = 1
                                final_darts[other_vertex][index2][axis] = -1
                            else:
                                final_darts[vertex + 1][index][axis] = -1
                                final_darts[other_vertex][index2][axis] = 1

                    else:
                        if abs(this_coords[axis] - other_coords[axis]) > map_size[axis] / 2:
                            if this_coords[axis] > map_size[axis] / 2:
                                final_darts[vertex + 1][index][axis] = 1
                                final_darts[other_vertex][index2][axis] = -1
                            else:
                                final_darts[vertex + 1][index][axis] = -1
                                final_darts[other_vertex][index2][axis] = 1
                        else:
                            final_darts[vertex + 1][index][axis] = 0
                            final_darts[other_vertex][index2][axis] = 0

    # Check no erroneous edges/darts have been added
    for vertex in graph_range:
        counter = 0
        for final_connection in final_graph[vertex + 1]:
            if final_connection not in source_graph[vertex + 1]:
                final_graph[vertex + 1].remove(final_connection)
                final_darts[vertex + 1].remove(final_darts[vertex + 1][counter])
            counter += 1

    return final_graph, final_coordinates, final_darts, embedded_coordinates
