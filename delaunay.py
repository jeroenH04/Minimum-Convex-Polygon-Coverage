import numpy as np
from typing import List
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import json


class Vertex:
    def __init__(self, x: int, y: int):
        """
        :param x: x-coordinate of the vertex
        :param y: y-coordinate of the vertex
        """
        self.x = x
        self.y = y


class Edge:
    def __init__(self, v1: Vertex, v2: Vertex):
        """
        :param v1: Vertex
        :param v2: Vertex
        """
        self.v1 = v1
        self.v2 = v2


class Triangle:
    def __init__(self, a: Vertex, b: Vertex, c: Vertex):
        """
        :param a: 1st vertex of the triangle
        :param b: 2nd vertex of the triangle
        :param c: 3rd vertex of the triangle
        """
        self.v: List[Vertex] = [a, b, c]
        self.edges: List[Edge] = [Edge(a, b), Edge(b, c), Edge(c, a)]

    def containsVertex(self, vertex: Vertex) -> bool:
        """
        Check if a vertex is part of the triangle

        :param vertex: vertex to be checked
        :return: whether vertex is part of the triangle
        """
        return (self.v[0] == vertex) or (self.v[1] == vertex) or (self.v[2] == vertex)


def calculateSuperTriangleVertices(vertices) -> List[Vertex]:
    minX = minY = float("inf")
    maxX = maxY = -float("inf")

    for x, y in vertices:
        minX = min(minX, x)
        minY = min(minX, y)
        maxX = max(maxX, x)
        maxY = max(maxX, y)

    vx = (maxX - minX) * 10
    vy = (maxY - minY) * 10

    superPointA = Vertex(minX - vx, minY - vy * 3)
    superPointB = Vertex(minX - vx, maxY + vy)
    superPointC = Vertex(maxX + vx * 3, maxY + vy)

    return [superPointA, superPointB, superPointC]


def isInCircumCircleOf(vertex: Vertex, triangle: Triangle):
    """
    Check if a vertex is in the circumcircle of a triangle
    :param vertex:
    :param triangle:
    :return: bool
    """
    # Calculate the coordinates of the vertices of the triangle
    ax, ay = triangle.v[0].x, triangle.v[0].y
    bx, by = triangle.v[1].x, triangle.v[1].y
    cx, cy = triangle.v[2].x, triangle.v[2].y
    vx, vy = vertex.x, vertex.y

    # Calculate the determinant of the matrix formed by the coordinates of the vertices.
    m = np.array([[ax - vx, ay - vy, (ax - vx) ** 2 + (ay - vy) ** 2],
                  [bx - vx, by - vy, (bx - vx) ** 2 + (by - vy) ** 2],
                  [cx - vx, cy - vy, (cx - vx) ** 2 + (cy - vy) ** 2]], dtype=float)

    return np.linalg.det(m) <= 0


def edgeIsSharedByOtherTriangles(edge: Edge, triangle: Triangle, triangles: List[Triangle]) -> bool:
    """
    Check if an edge is shared by another triangle

    :param edge: Edge to be checked
    :param triangle: Original triangle
    :param triangles: Set of of other triangles, possibly containing `triangle`
    :return: edge is shared by another triangle
    """
    for otherTriangle in triangles:
        if triangle == otherTriangle:
            continue
        for otherEdge in otherTriangle.edges:
            if (edge.v1 == otherEdge.v1 and edge.v2 == otherEdge.v2) or \
                    (edge.v1 == otherEdge.v2 and edge.v2 == otherEdge.v1):
                return True

    return False


class DelaunayTriangulation:
    def __init__(self, vertices, name):
        """
        Initialize Delaunay Triangulation by calculating the super triangle for the Bowyer Watson algorithm

        :param vertices: vertices to be triangulated
        """
        self.name = name
        self.triangulation = []

        self.superPointA, self.superPointB, self.superPointC = calculateSuperTriangleVertices(vertices)
        self.triangulation.append(Triangle(self.superPointA, self.superPointB, self.superPointC))

        self.triangulate(vertices)

    def triangulate(self, vertices):
        """
        Triangulate the given vertices using the Bowyer Watson algorithm
        https://en.wikipedia.org/wiki/Bowyer%E2%80%93Watson_algorithm

        :param vertices:
        """
        # Incrementally add vertices to the triangulation
        for x, y in vertices:
            self.addVertex(Vertex(x, y))

        for triangle in self.triangulation[:]:
            # Remove super triangle from triangulation
            if triangle.containsVertex(self.superPointA) or triangle.containsVertex(self.superPointB) or \
                    triangle.containsVertex(self.superPointC):
                self.triangulation.remove(triangle)

    def addVertex(self, vertex: Vertex):
        """
        :param vertex: vertex to be added to the triangulation
        :param prevVertex: previous handled vertex
        """
        # Create empty set of triangles that are no longer valid
        badTriangles = []

        # Find all triangles that are no longer valid due to the insertion of the vertex
        for triangle in self.triangulation:
            # Check if the given point is inside the circumcircle of the triangle
            if isInCircumCircleOf(vertex, triangle):
                badTriangles.append(triangle)

        polygon = []
        # Find the boundary of the polygonal hole
        for triangle in badTriangles:
            for edge in triangle.edges:
                if not edgeIsSharedByOtherTriangles(edge, triangle, badTriangles):
                    polygon.append(edge)

        # Remove the bad triangles from the data structure
        for triangle in badTriangles:
            self.triangulation.remove(triangle)

        # Re-triangulate the polygonal hole
        for edge in polygon:
            self.triangulation.append(Triangle(edge.v1, edge.v2, vertex))

    def plot(self):
        ps = []
        for t in self.triangulation:
            for p in t.v:
                ps.append(p)

        x_s = [p.x for p in ps]
        y_s = [p.y for p in ps]

        ts = []
        for t in self.triangulation:
            ts.append((ps.index(t.v[0]), ps.index(t.v[1]), ps.index(t.v[2])))

        fig, ax = plt.subplots()
        ax.triplot(tri.Triangulation(x_s, y_s, ts), 'bo--')
        ax.set_title('Plot of Delaunay triangulation')

        plt.show()

    def export(self):
        export = {
            "type": "CGSHOP2023_Solution",
            "instance": self.name,
            "polygons": []
        }

        for triangle in self.triangulation:
            export['polygons'].append([
                {'x': triangle.v[0].x, 'y': triangle.v[0].y},
                {'x': triangle.v[1].x, 'y': triangle.v[1].y},
                {'x': triangle.v[2].x, 'y': triangle.v[2].y}
            ])

        # Serializing json
        json_object = json.dumps(export, indent=4)

        # Writing to sample.json
        with open(self.name + "-sol" + ".json", "w") as outfile:
            outfile.write(json_object)
