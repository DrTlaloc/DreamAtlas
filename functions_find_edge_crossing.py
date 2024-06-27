from . import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# point q lies on line segment 'pr'
def on_segment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Collinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0


# The main function that returns true if
# the line segment 'p1q1' and 'p2q2' intersect.
def do_intersect(p1, q1, p2, q2):
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # Check the points don't meet
    # p1 and p2 meet but q1 and q2 do not
    if (p1.x == p2.x and p1.y == p2.y) and not (q1.x == q2.x and q1.y == q2.y):
        return False
    # p1 and q2 meet but q1 and p2 do not
    if (p1.x == q2.x and p1.y == q2.y) and not (q1.x == p2.x and q1.y == p2.y):
        return False
    # q1 and p2 meet but p1 and q2 do not
    if (q1.x == p2.x and q1.y == p2.y) and not (p1.x == q2.x and p1.y == q2.y):
        return False
    # q1 and q2 meet but p1 and p2 do not
    if (q1.x == q2.x and q1.y == q2.y) and not (p1.x == p2.x and p1.y == p2.y):
        return False

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and on_segment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and on_segment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and on_segment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and on_segment(p2, q1, q2):
        return True

    # If none of the cases
    return False

# ^^^ This section of code is contributed by Ansh Riyal


def edge_crossing_detection(virtual_graph, virtual_coordinates):

    edge_crossings = 0

    edges = []
    for vertex in range(len(virtual_graph)):
        x1, y1 = virtual_coordinates[vertex + 1]
        for connection in virtual_graph[vertex + 1]:
            x2, y2 = virtual_coordinates[connection]
            edge = [x1, y1, x2, y2]
            if [x2, y2, x1, y1] not in edges:
                edges.append(edge)

    checks = []
    for edge1 in edges:
        p1 = Point(edge1[0], edge1[1])
        q1 = Point(edge1[2], edge1[3])
        for edge2 in edges:
            p2 = Point(edge2[0], edge2[1])
            q2 = Point(edge2[2], edge2[3])
            check = [p1, q1, p2, q2]
            if [p2, q2, p1, q1] not in checks:
                checks.append(check)
                if do_intersect(p1, q1, p2, q2):
                    edge_crossings += 1

    return edge_crossings
