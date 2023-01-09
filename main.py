import delaunay as d
import earclipping as e
import dll as dll
import hm as hm
import json
from typing import List


def loadJSON(instanceName):
    # Load the instance json
    with open(f'instances/{instanceName}.json', 'r') as f:
        instance = json.load(f)

    return instance


# Mapper for object coordinates to tuple
def pointMap(o):
    return o["x"], o["y"]


def ccw(x1, y1, x2, y2, x3, y3):
    """Returns True if the points (x2, y2) and (x3, y3) are counterclockwise
    with respect to (x1, y1), and False otherwise.
    """
    a = x2 - x1
    b = y2 - y1
    c = x3 - x1
    d = y3 - y1
    return a * d > b * c


def direction(a: dll.Vertex, b: dll.Vertex, c: dll.Vertex):
    val = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
    if val == 0:
        return 0  # Colinear
    elif val < 0:
        return 2  # CCW
    return 1  # CW


def linesIntersect(v1: dll.Vertex, v2: dll.Vertex, v3: dll.Vertex, v4: dll.Vertex):
    dir1 = direction(v1, v2, v3)
    dir2 = direction(v1, v2, v3)
    dir3 = direction(v3, v4, v1)
    dir4 = direction(v3, v4, v2)

    return dir1 != dir2 and dir3 != dir4


def getTriangleData(instanceName):
    instance = loadJSON(instanceName)
    verticesDoublyLinkedList = dll.DoublyLinkedList()

    outer_boundary = instance["outer_boundary"]
    outer_boundary = list(map(pointMap, outer_boundary))

    n = len(outer_boundary)
    for idx, v in enumerate(outer_boundary):
        verticesDoublyLinkedList.insertAtEnd(dll.Vertex(v[0], v[1], 0), idx == n - 1)

    for hole in instance["holes"]:
        """
        Create pairs between the inner vertices and the outer vertices
        based on `Ear-Clipping Based Algorithms of Generating High-quality Polygon Triangulation` by Mei, Gang et al
        """
        pairs: List[dll.Vertex, dll.Vertex, float] = []
        innerVerticesDoublyLinkedList = dll.DoublyLinkedList()

        inner_boundary = list(map(pointMap, hole))
        n = len(inner_boundary)
        for idx, v in enumerate(inner_boundary):
            innerVertex = dll.Vertex(v[0], v[1])
            innerVerticesDoublyLinkedList.insertAtEnd(innerVertex, idx == n - 1)

            outerIdx = 0
            outerVertex = verticesDoublyLinkedList.head
            while outerIdx < verticesDoublyLinkedList.length():
                # Calculate distance
                distance = innerVertex.calculateDistance(outerVertex.vertex)
                pairs.append([innerVertex, outerVertex.vertex, distance])

                outerVertex = outerVertex.next
                outerIdx += 1

        pairs.sort(key=lambda pair: pair[2], reverse=True)
        found = False
        innerBridge, outerBridge = None, None

        while not found:
            intersect = False

            # Get bridge candidate: pair with shortest distance
            bridgeCandidate = pairs.pop()
            innerBridge, outerBridge = bridgeCandidate[0], bridgeCandidate[1]

            # Check if any outer intersects the bridge candidate
            outerIdx = 0
            outerVertex = verticesDoublyLinkedList.head
            while outerIdx < verticesDoublyLinkedList.length():
                if linesIntersect(innerBridge, outerBridge, outerVertex.vertex, outerVertex.next.vertex):
                    intersect = True
                    break

                outerVertex = outerVertex.next
                outerIdx += 1

            if intersect:
                # If the bridge candidate intersected with one of the outer edges, reject this candidate
                continue

            for idx, v in enumerate(inner_boundary):
                innerVertex = dll.Vertex(v[0], v[1])
                nextInnerVertex = dll.Vertex(inner_boundary[(idx + 1) % n][0], inner_boundary[(idx + 1) % n][1])
                if linesIntersect(innerBridge, outerBridge, innerVertex, nextInnerVertex):
                    intersect = True
                    break

            if not intersect:
                found = True

        # Add bridge to the outer polygon
        outerIdx = 0
        outerVertex = verticesDoublyLinkedList.head
        outerLength = verticesDoublyLinkedList.length()
        while outerIdx < outerLength:
            # Search for the outer vertex of the bridge
            if outerVertex.vertex == outerBridge:

                # Search for the inner vertex of the bridge
                innerIdx = 0
                innerVertex = innerVerticesDoublyLinkedList.head
                while innerIdx < outerLength:

                    # Search for the outer vertex of the bridge
                    if innerVertex.vertex == innerBridge:
                        # Connect inner DLL to outer DLL
                        outerVertexCopy = dll.Node(dll.Vertex(outerVertex.vertex.x, outerVertex.vertex.y))
                        innerVertexCopy = dll.Node(dll.Vertex(innerVertex.vertex.x, innerVertex.vertex.y))

                        outerVertexCopy.previous = outerVertex.previous
                        outerVertexCopy.next = innerVertexCopy
                        outerVertex.previous.next = outerVertexCopy

                        innerVertexCopy.previous = outerVertexCopy
                        innerVertexCopy.next = innerVertex.next
                        innerVertex.next.previous = innerVertexCopy

                        innerVertex.next = outerVertex
                        outerVertex.previous = innerVertex

                        verticesDoublyLinkedList.size += innerVerticesDoublyLinkedList.length() + 2

                        break

                    innerVertex = innerVertex.next
                    innerIdx += 1

            outerVertex = outerVertex.next
            outerIdx += 1

    return verticesDoublyLinkedList


instance_name = "srpg_iso_aligned_mc0001336" + ".instance"
vertices = getTriangleData(instance_name)

# Useful for debugging:
# i = 0
# o = vertices.head
# while i < vertices.length():
#     print('vertex: ' + str(o.vertex.x) + ', ' + str(o.vertex.y) + ' '
#           'next: ' + str(o.next.vertex.x) + ', ' + str(o.next.vertex.y) + ' '
#           'previous: ' + str(o.previous.vertex.x) + ', ' + str(o.previous.vertex.y)
#           )
#     o = o.next
#     i += 1

# DT = d.DelaunayTriangulation(vertices, instance_name)
# DT.plot()

DT = e.EarClipping(vertices, instance_name)
print(len(DT.triangulation), 'triangles')
HM = hm.HertelMehlhorn(DT)
#HM.DT.plot()
HM.plot(HM)
HM.export(HM)
