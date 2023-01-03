import gc
import math


class Vertex:
    def __init__(self, x: int, y: int, angle=0.0):
        """
        :param x: x-coordinate of the vertex
        :param y: y-coordinate of the vertex
        :param angle: angle of the vertex within the polygon
        """
        self.x = x
        self.y = y
        self.angle = angle

    # def __eq__(self, other):
    #     return self.x == other.x and self.y == other.y and self.angle == other.angle

    def calculateDistance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Node:
    def __init__(self, vertex: Vertex):
        """
        :param vertex:
        """
        self.previous = None
        self.vertex = vertex
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def isEmpty(self) -> bool:
        """
        Check if the DLL is empty
        :return: bool
        """
        if self.head is None:
            return True
        return False

    def insertAtBeginning(self, value: Vertex):
        """
        Insert a Vertex at the beginning of the DLL
        :param value: Vertex
        """
        self.size += 1
        new_node = Node(value)
        if self.isEmpty():
            self.head = new_node
        else:
            new_node.next = self.head
            self.head.previous = new_node
            self.head = new_node

    def insertAtEnd(self, value, finalNode=False):
        """
        Insert a Vertex at the end of the DLL
        :param value: Vertex
        :param finalNode: whether this node is the final node to be added, to make the DLL circular
        """
        new_node = Node(value)
        if self.isEmpty():
            self.insertAtBeginning(value)
        else:
            self.size += 1
            temp = self.head
            while temp.next is not None:
                temp = temp.next
            temp.next = new_node
            new_node.previous = temp
            if finalNode:
                new_node.next = self.head
                self.head.previous = new_node

    def deleteFromLast(self):
        """
        Delete the last element from the DLL
        """
        self.size -= 1
        if self.isEmpty():
            print("Linked List is empty. Cannot delete elements.")
        elif self.head.next is None:
            self.head = None
        else:
            temp = self.head
            while temp.next is not None:
                temp = temp.next
            temp.previous.next = None
            temp.previous = None

        gc.collect()

    def delete(self, value: Vertex):
        """
        Delete `value` from the DLL
        :param value: Vertex
        """
        if self.isEmpty():
            print("Linked List is empty. Cannot delete elements.")
        elif self.head.next is None:
            self.size -= 1
            if self.head.vertex == value:
                self.head = None
        else:
            self.size -= 1
            temp = self.head
            idx = 0
            while temp is not None:
                if temp.vertex == value:
                    break
                temp = temp.next
                idx += 1

            if temp is None:
                print("Element not present in linked list. Cannot delete element.")
            elif temp.next is None:
                self.deleteFromLast()
            else:
                temp.previous.next = temp.next
                temp.next.previous = temp.previous

        gc.collect()

    def length(self):
        return self.size
