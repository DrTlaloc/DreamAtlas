import numpy as np
from numba import njit
from numba.experimental import jitclass
from DreamAtlas import find_graph_faces
from DreamAtlas.functions import make_virtual_graph


# @jitclass
class DreamGraph:

    def __init__(self, size, map_size):

        self.graph = np.zeros((size, size), dtype=np.bool_)
        self.coordinates = np.zeros((size, 2), dtype=np.int32)
        self.darts = np.zeros((size, size, 2), dtype=np.int8)
        self.map_size = map_size

    def add_node(self):  # Adds a node to the graph

        x = 1

    def connect_nodes(self):

        x = 1

    def insert_node(self, i, j, k, kx, ky):  # Inserts a new node between two existing nodes

        self.graph[i, j] = 0
        self.graph[j, i] = 0
        self.graph[i, k] = 1
        self.graph[k, i] = 1
        self.graph[j, k] = 1
        self.graph[k, j] = 1

    def get_length(self, i, j):

        return np.linalg.norm(self.coordinates[j] + self.darts[i, j] * self.map_size - self.coordinates[i])

    def get_faces_centroids(self):

        edges_set, embedding = set(), dict()
        for i in self.graph:  # edges_set is an undirected graph as a set of undirected edges
            j_angles = list()
            for j in self.graph[i]:
                edges_set |= {(i, j), (j, i)}
                vector = self.coordinates[j] + np.multiply(self.darts[i][self.graph[i].index(j)], self.map_size) - self.coordinates[i]
                angle = 90 - np.angle(vector[0] + vector[1] * 1j, deg=True)
                j_angles.append([j, angle])

            j_angles.sort(key=lambda x: x[1])
            embedding[i] = [x[0] for x in
                            j_angles]  # Format: v1:[v2,v3], v2:[v1], v3:[v1] clockwise ordering of neighbors at each vertex

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
                for edge in edges_set:  # Starts next path
                    path.append(edge)
                    edges_set -= {edge}
                    break  # Only one iteration
            else:
                path.append(tup)
                edges_set -= {tup}
        if len(path) != 0:
            faces.append(path)

        centroids = list()
        for face in faces:
            shift = np.subtract(np.divide(self.map_size, 2), self.coordinates[face[0][0]])
            total = np.zeros(2)
            for edge in face:
                i = edge[0]
                total += (np.add(self.coordinates[i], shift)) % self.map_size
            coordinate = (-shift + total / len(face)) % self.map_size
            centroids.append((int(coordinate[0]), int(coordinate[1])))

        return faces, centroids

    def get_virtual_graph(self):

        virtual_graph, virtual_coordinates = dict(), self.coordinates
        for i in self.graph:
            virtual_graph[i] = list()
            virtual_coordinates[i] = self.coordinates[i]

        new_index = max(self.graph) + 1
        done_edges = {(-1, -1)}
        for i in self.graph:
            for j_index in range(len(self.graph[i])):
                j = self.graph[i][j_index]
                if (i, j) not in done_edges:  # If we haven't done this connection continue
                    done_edges.add((j, i))
                    dart_x, dart_y = self.darts[i][j_index]

                    if dart_x == 0 and dart_y == 0:  # If the connection does not cross the torus then just add the edge
                        virtual_graph[i].append(j)
                        virtual_graph[j].append(i)
                    else:  # Otherwise we need to find the virtual coordinates
                        vector = self.coordinates[j] + self.darts[i][j_index] * np.asarray(self.mapsize) - self.coordinates[i]
                        unit_vector = vector / np.linalg.norm(vector)

                        infinite_coordinates = list()  # Find the infinite edge points
                        for axis in range(2):
                            if self.darts[i][j_index][axis] == -1:
                                ic = 0
                            elif self.darts[i][j_index][axis] == 1:
                                ic = self.mapsize[axis]
                            else:
                                continue
                            if axis == 0:
                                infinite_coordinates.append([ic, self.coordinates[i][1] + (ic - self.coordinates[i][0]) * unit_vector[1] / unit_vector[0]])
                            else:
                                infinite_coordinates.append([self.coordinates[i][0] + (ic - self.coordinates[i][1]) * unit_vector[0] / unit_vector[1], ic])

                        if len(infinite_coordinates) == 2:  # Find which is closer and build virtual graph
                            virtual_graph[i].append(new_index)  # 1st node to 1st edge
                            virtual_graph[new_index] = [i]
                            virtual_coordinates[new_index] = infinite_coordinates[0]

                            virtual_graph[new_index + 1] = [new_index + 2]  # 1st edge to 2nd edge
                            virtual_graph[new_index + 2] = [new_index + 1]
                            if np.linalg.norm(np.subtract(self.coordinates[i], infinite_coordinates[0])) > np.linalg.norm(np.subtract(self.coordinates[i], infinite_coordinates[1])):  # seeing which is closer
                                infinite_coordinates = [infinite_coordinates[1], infinite_coordinates[0]]
                                virtual_coordinates[new_index + 1] = [infinite_coordinates[0][0], infinite_coordinates[0][1] - dart_y * self.mapsize[1]]
                                virtual_coordinates[new_index + 2] = [infinite_coordinates[1][0], infinite_coordinates[1][1] - dart_y * self.mapsize[1]]
                            else:
                                infinite_coordinates = [infinite_coordinates[0], infinite_coordinates[1]]
                                virtual_coordinates[new_index + 1] = [infinite_coordinates[0][0] - dart_x * self.mapsize[0], infinite_coordinates[0][1]]
                                virtual_coordinates[new_index + 2] = [infinite_coordinates[1][0] - dart_x * self.mapsize[0], infinite_coordinates[1][1]]

                            virtual_graph[new_index + 3] = [j]  # 2nd edge to 2nd node
                            virtual_graph[j].append(new_index + 3)
                            virtual_coordinates[new_index + 3] = [infinite_coordinates[1][0] - dart_x * self.mapsize[0], infinite_coordinates[1][1] - dart_y * self.mapsize[1]]
                        else:
                            virtual_graph[i].append(new_index)  # Vertex to edge
                            virtual_graph[new_index] = [i]
                            virtual_coordinates[new_index] = infinite_coordinates[0]
                            virtual_graph[new_index + 1] = [j]  # Edge to connection
                            virtual_graph[j].append(new_index + 1)
                            virtual_coordinates[new_index + 1] = [infinite_coordinates[0][0] - dart_x * self.mapsize[0], infinite_coordinates[0][1] - dart_y * self.mapsize[1]]

                        new_index += 2 * len(infinite_coordinates)

        return virtual_graph, virtual_coordinates
