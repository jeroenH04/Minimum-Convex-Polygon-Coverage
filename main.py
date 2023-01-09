import earclipping as e
import dll as dll
import hm as hm
import json
from typing import List
from datetime import datetime


def loadJSON(instanceName):
    # Load the instance json
    with open(f'instances/{instanceName}.json', 'r') as f:
        instance = json.load(f)

    return instance


# Mapper for object coordinates to tuple
def pointMap(o):
    return o["x"], o["y"]


def direction(a: dll.Vertex, b: dll.Vertex, c: dll.Vertex) -> int:
    """
    :param a: Vertex
    :param b: Vertex
    :param c: Vertex
    :return: bool
    """
    val = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
    if val == 0:
        return 0  # Colinear
    elif val < 0:
        return 2  # CCW
    return 1  # CW


def linesIntersect(a: dll.Vertex, b: dll.Vertex, c: dll.Vertex, d: dll.Vertex, soft=True) -> bool:
    """
    Check if the line (a,b) intersects the line (c,d)
    :param soft: bool
    :param a: Vertex
    :param b: Vertex
    :param c: Vertex
    :param d: Vertex
    :return: bool
    """
    if soft and (a.x == c.x and a.y == c.y) or (a.x == d.x and a.y == d.y) or \
            (b.x == c.x and b.y == c.y) or (b.x == d.x and b.y == d.y):
        return False

    dir1 = direction(a, b, c)
    dir2 = direction(a, b, d)
    dir3 = direction(c, d, a)
    dir4 = direction(c, d, b)

    return dir1 != dir2 and dir3 != dir4


def getTriangleData(instanceName):
    """
    :param instanceName: string
    :return: dll.DoublyLinkedList()
    """
    instance = loadJSON(instanceName)
    verticesDoublyLinkedList = dll.DoublyLinkedList()

    outer_boundary = instance["outer_boundary"]
    outer_boundary = list(map(pointMap, outer_boundary))

    n = len(outer_boundary)
    for idx, v in enumerate(outer_boundary):
        verticesDoublyLinkedList.insertAtEnd(dll.Vertex(v[0], v[1], 0), idx == n - 1)

    holes = instance["holes"]

    # Add holes to the polygon
    for hole in holes:
        """
        Create pairs between the inner vertices and the outer vertices to find bridge candidates
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

        # Sort the bridge candidate pairs on distance
        pairs.sort(key=lambda pair: pair[2], reverse=True)
        found, noPairs = False, False
        innerBridge, outerBridge = None, None

        while not found:
            if len(pairs) == 0:
                # If there are no pairs anymore for this hole, add it to the end
                # and continue with another hole
                holes.append(hole)
                noPairs = True
                break

            intersect = False

            # Get bridge candidate: pair with shortest distance
            bridgeCandidate = pairs.pop()
            innerBridge, outerBridge = bridgeCandidate[0], bridgeCandidate[1]

            if outerBridge.isCopied and len(pairs) > 0:
                # The bridge candidate was copied, check whether this or the equivalent vertex should be picked
                intersect2 = False
                i = 0
                temp = verticesDoublyLinkedList.head
                while i < verticesDoublyLinkedList.length():
                    if temp.vertex.x == outerBridge.x and temp.vertex.y == outerBridge.y:
                        # Check if any outer edge intersects the bridge candidate
                        outerIdx = 0
                        outerVertex = verticesDoublyLinkedList.head
                        while outerIdx <= verticesDoublyLinkedList.length():
                            if temp.next.vertex.isCopied or temp.previous.vertex.isCopied:
                                intersect = True
                                break

                            if linesIntersect(innerBridge, temp.next.vertex, outerVertex.vertex,
                                              outerVertex.next.vertex) or \
                                    linesIntersect(innerBridge, temp.previous.vertex, outerVertex.vertex,
                                                   outerVertex.next.vertex):
                                if intersect2:
                                    # Both copies of the bridge candidate intersect
                                    intersect = True
                                # The current bridge candidate intersects
                                intersect2 = True
                                break

                            outerVertex = outerVertex.next
                            outerIdx += 1

                        if not intersect2:
                            # This copy did not intersect anything, so reset the outer bridge
                            outerBridge = temp.vertex
                            break

                    temp = temp.next
                    i += 1

            # Check if any outer edge intersects the bridge candidate
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

            for hole2 in instance["holes"]:
                inner_boundary2 = list(map(pointMap, hole2))
                n = len(inner_boundary2)
                for idx, v in enumerate(inner_boundary2):
                    # Check if any of the inner edge intersect the bridge candidate
                    innerVertex = dll.Vertex(v[0], v[1])
                    nextInnerVertex = dll.Vertex(inner_boundary2[(idx + 1) % n][0], inner_boundary2[(idx + 1) % n][1])
                    if linesIntersect(innerBridge, outerBridge, innerVertex, nextInnerVertex):
                        intersect = True
                        break

                if intersect:
                    break

            if not intersect:
                found = True

        if noPairs:
            continue

        outerIdx = 0
        outerVertex = verticesDoublyLinkedList.head
        outerLength = verticesDoublyLinkedList.length()

        # Add bridge to the outer polygon
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
                        outerVertexCopy = dll.Node(dll.Vertex(outerVertex.vertex.x, outerVertex.vertex.y, 0.0, True))
                        innerVertexCopy = dll.Node(dll.Vertex(innerVertex.vertex.x, innerVertex.vertex.y, 0.0, True))

                        outerVertexCopy.previous = outerVertex.previous
                        outerVertexCopy.next = innerVertexCopy
                        outerVertex.previous.next = outerVertexCopy
                        outerVertex.vertex.isCopied = True

                        innerVertexCopy.previous = outerVertexCopy
                        innerVertexCopy.next = innerVertex.next
                        innerVertex.next.previous = innerVertexCopy
                        innerVertex.vertex.isCopied = True

                        innerVertex.next = outerVertex
                        outerVertex.previous = innerVertex

                        verticesDoublyLinkedList.size += innerVerticesDoublyLinkedList.length() + 2

                        break

                    innerVertex = innerVertex.previous
                    innerIdx += 1

            outerVertex = outerVertex.next
            outerIdx += 1

    return verticesDoublyLinkedList


def main(instance_name: str, plot=True, export=True):
    timestamp = datetime.now()
    print('Started creating doubly linked list...')
    instance_name = instance_name + ".instance"
    vertices = getTriangleData(instance_name)
    print('Created doubly linked list in: ', datetime.now() - timestamp)

    print('Start triangulation...')
    timestamp = datetime.now()
    T = e.EarClipping(vertices, instance_name)
    print('Created triangulation in: ', datetime.now() - timestamp, 'with ', len(T.triangulation), ' triangles')

    print('Start Hertel Mehlhorn...')
    timestamp = datetime.now()
    HM = hm.HertelMehlhorn(T)
    print('Executed Hertel Mehlhorn in: ', datetime.now() - timestamp, 'resulting in ', len(HM.polygons), ' polygons')

    if plot:
        T.plot()
        HM.plot()
    if export:
        T.export()
        HM.export()


main('srpg_smo_mc0005962')
