import delaunay as d
import earclipping as e
import dll as dll
import json


def loadJSON(instanceName):
    # Load the instance json
    with open(f'instances/{instanceName}.json', 'r') as f:
        instance = json.load(f)

    return instance


# Mapper for object coordinates to tuple
def pointMap(o):
    return o["x"], o["y"]


def getTriangleData(instanceName):
    instance = loadJSON(instanceName)
    verticesDoublyLinkedList = dll.DoublyLinkedList()

    outer_boundary = instance["outer_boundary"]
    outer_boundary = list(map(pointMap, outer_boundary))

    n = len(outer_boundary)
    for idx, v in enumerate(outer_boundary):
        verticesDoublyLinkedList.insertAtEnd(dll.Vertex(v[0], v[1], 0), idx == n - 1)

        # if idx == len(outer_boundary) - 1:
        #     # Connect the last vertex to the first vertex of the outer_boundary
        #     segments.append([idx, 0])
        # else:
        #     segments.append([idx, idx + 1])
        #
        # index += 1

    # for hole in instance["holes"]:
    #     x = []
    #     y = []
    #     inner_boundary = list(map(pointMap, hole))
    #     for idx, v in enumerate(inner_boundary):
    #         vertices.append([v[0], v[1]])
    #         x.append(v[0])
    #         y.append(v[1])
    #
    #         if idx == len(inner_boundary) - 1:
    #             # Connect the last vertex to the first vertex of this inner boundary
    #             segments.append([index, index - len(inner_boundary) + 1])
    #         else:
    #             segments.append([index, index + 1])
    #
    #         index += 1
    #
    #     # Calculate the centroid of the hole
    #     centroid = [sum(x) / len(inner_boundary), sum(y) / len(inner_boundary)]
    #     holes.append(centroid)

    return verticesDoublyLinkedList


instance_name = "example_instance1" + ".instance"
vertices = getTriangleData(instance_name)

# DT = d.DelaunayTriangulation(vertices, instance_name)
# DT.plot()

DT = e.EarClipping(vertices, instance_name)
DT.plot()
# DT.export()




