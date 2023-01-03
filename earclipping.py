import numpy as np
import dll as dll
from typing import List
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import json
import math


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

    def containsVertex(self, vertex: dll.Vertex) -> bool:
        """
        Check if a vertex is part of the triangle

        :param vertex: vertex to be checked
        :return: whether vertex is part of the triangle
        """
        return (self.v[0] == vertex) or (self.v[1] == vertex) or (self.v[2] == vertex)


class EarClipping:
    def __init__(self, vertices: dll.DoublyLinkedList, name: str):
        """
        :param vertices: DLL of the vertices of the polygon
        :param name: name of the instance
        """
        self.name = name
        self.triangulation = []
        self.vertices = vertices
        self.earTips = []

        self.triangulate()

    def getAngle(self, a: dll.Vertex, b: dll.Vertex, c: dll.Vertex):
        """
        Calculate the angle between 3 vertices, and add it to the eartips list if the angle is convex
        :param a: Vertex
        :param b: Vertex
        :param c: Vertex
        :return: angle
        """
        ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
        ang = ang + 360 if ang < 0 else ang

        if ang < 180:
            # Convex
            self.earTips.append(b)

        return ang

    def triangulate(self):
        """
        Triangulate simple polygon using ear clipping
        based on `Ear-Clipping Based Algorithms of Generating High-quality Polygon Triangulation` by Mei, Gang et al
              and `Triangulation by Ear Clipping` by Eberly, David et al.
        """
        n = self.vertices.length()
        v = self.vertices.head
        idx = 0

        # Calculate angles of all vertices in DLL and collect convex vertices
        while idx < self.vertices.length():
            if v.previous and v.next:
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
