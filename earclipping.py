import dll as dll
from typing import List
import matplotlib.pyplot as plt
import json
import math
from copy import copy
import sys, threading
sys.setrecursionlimit(10**7) # max depth of recursion
threading.stack_size(2**27)  # new thread will get stack of such size


class Edge:
    def __init__(self, v1: dll.Vertex, v2: dll.Vertex):
        """
        :param v1: dll.Vertex
        :param v2: dll.Vertex
        """
        self.v1 = v1
        self.v2 = v2


class Triangle:
    def __init__(self, a: dll.Vertex, b: dll.Vertex, c: dll.Vertex):
        """
        :param a: 1st vertex of the triangle
        :param b: 2nd vertex of the triangle
        :param c: 3rd vertex of the triangle
        """
        self.v: List[dll.Vertex] = [a, b, c]
        self.edges: List[Edge] = [Edge(a, b), Edge(b, c), Edge(c, a)]
        self.area = areaOfTriangle(a, b, c)


def areaOfTriangle(a: dll.Vertex, b: dll.Vertex, c: dll.Vertex) -> float:
    """
    Calculate the area of a triangle
    :param a: Vertex
    :param b: Vertex
    :param c: Vertex
    :return: float
    """
    return abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0)


def isInside(a: dll.Vertex, b: dll.Vertex, c: dll.Vertex, d: dll.Vertex) -> bool:
    """
    Check if vertex d is inside the triangle (a,b,c).
    If d only touches the triangle, it is not considered to be inside
    :param a: Vertex
    :param b: Vertex
    :param c: Vertex
    :param d: Vertex
    :return: bool
    """
    if (d.x == a.x and d.y == a.y) or (d.x == b.x and d.y == b.y) or (d.x == c.x and d.y == c.y):
        return False

    A = areaOfTriangle(a, b, c)
    A1 = areaOfTriangle(d, b, c)
    A2 = areaOfTriangle(a, d, c)
    A3 = areaOfTriangle(a, b, d)

    return math.isclose(A, A1 + A2 + A3, rel_tol=1e-5)


class EarClipping:
    def __init__(self, vertices: dll.DoublyLinkedList, name: str):
        """
        :param vertices: DLL of the vertices of the polygon
        :param name: name of the instance
        """
        self.name = name
        self.triangulation = []
        self.vertices = vertices
        self.allVertices = copy(vertices)
        self.earTips = []
        self.triangulate()

    def getAngle(self, a: dll.Vertex, b: dll.Vertex, c: dll.Vertex):
        """
        Calculate the angle between (a, b, c).
        Add b to the list of ear tips if the angle is convex and the closure of the triangle (a,b,c)
        does not contain any vertex of the polygon
        :param a: Vertex
        :param b: Vertex
        :param c: Vertex
        :return: angle
        """
        containsPoint = False

        ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
        ang = ang + 360 if ang < 0 else ang

        if ang < 180:  # Convex
            idx = 0
            v = self.allVertices.head
            while idx < self.allVertices.length():
                if isInside(a, b, c, v.vertex):
                    # Check if the closure of the triangle does not contain any (reflex) vertex of P
                    containsPoint = True
                    break

                v = v.next
                idx += 1

            if not containsPoint:
                self.earTips.append(b)

        return ang

    def triangulate(self):
        """
        Triangulate simple polygon using ear clipping
        based on `Ear-Clipping Based Algorithms of Generating High-quality Polygon Triangulation` by Mei, Gang et al
        """
        n = self.vertices.length()

        v = self.vertices.head
        idx = 0

        # Calculate angles of all vertices in DLL and collect convex vertices
        while idx < self.vertices.length():
            angle = self.getAngle(v.next.vertex, v.vertex, v.previous.vertex)
            v.vertex.angle = angle

            v = v.next
            idx += 1

        # Continue cutting of ear tips as long as there are ear tips left, and we have less than n - 2 triangles
        while len(self.triangulation) < n - 2 and len(self.earTips) > 0:
            # Sort the ear tips in descending order, such that the last item holds the ear tip with the smallest angle
            self.earTips.sort(key=lambda vertex: vertex.angle, reverse=True)
            earTip = self.earTips.pop()

            temp = self.vertices.head
            idx = 0

            # Loop over the DLL to find the location of the ear tip
            while temp is not None and idx < n:
                if temp.vertex == earTip:
                    prevVertex = temp.previous
                    nextVertex = temp.next

                    # Add the ear to the triangulation
                    self.triangulation.append(Triangle(prevVertex.vertex, temp.vertex, nextVertex.vertex))

                    # Remove the ear tip from the DLL
                    self.vertices.delete(temp.vertex)

                    # Remove the previous and next vertex from the ear tips, as they will be recalculated
                    if prevVertex.vertex in self.earTips:
                        self.earTips.remove(prevVertex.vertex)

                    if nextVertex.vertex in self.earTips:
                        self.earTips.remove(nextVertex.vertex)

                    # Update angles of v_prev and v_next
                    prevVertex.vertex.angle = self.getAngle(prevVertex.next.vertex, prevVertex.vertex, prevVertex.previous.vertex)
                    nextVertex.vertex.angle = self.getAngle(nextVertex.next.vertex, nextVertex.vertex, nextVertex.previous.vertex)
                    break

                idx += 1
                temp = temp.next

        if len(self.earTips) == 3:
            # If there are still 3 ear tips left, add them as a triangle
            self.triangulation.append(Triangle(self.earTips[0], self.earTips[1], self.earTips[2]))

    def plot(self):
        """
        Plot the triangulation
        """
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

        ax.scatter(x_s, y_s)
        for t in self.triangulation:
            x_p = [p.x for p in t.v]
            y_p = [p.y for p in t.v]
            ax.fill(x_p, y_p)
        ax.set_title('Triangulation ' + self.name)
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
