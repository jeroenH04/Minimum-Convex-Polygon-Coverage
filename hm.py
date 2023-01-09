import dll as dll
from typing import List
from earclipping import Edge
import matplotlib.pyplot as plt
import json

class Polygon:
    def __init__(self, vertices: List[dll.Vertex], edges: List[Edge]):
        """
        :param a: 1st vertex of the triangle
        :param b: 2nd vertex of the triangle
        :param c: 3rd vertex of the triangle
        """
        self.v: List[dll.Vertex] = vertices
        self.edges: List[Edge] = edges
    
    def getNumPoints(self):
        return len(self.v)

    def getPoint(self, idx):
        return self.v[idx]

class HertelMehlhorn:
    def __new__(self, DT):
        """
        :param DT: triangulation of the polygon
        """
        self.DT = DT
        self.triangulation = DT.triangulation
        self.polygons = []

        for t in self.triangulation:
            self.polygons.append(Polygon(t.v, t.edges))

        return self.decompose(self)

    def isConvex(p1,p2,p3):
        tmp = (p3.y - p1.y) * (p2.x - p1.x) - (p3.x - p1.x) * (p2.y - p1.y);
        if tmp > 0:
            return True;
        else:
            return False;

    def decompose(self):

        #for every triangle:
        t1 = 0
        while t1 < len(self.polygons):
            polygon1 = self.polygons[t1]
            for i11 in range(polygon1.getNumPoints()):
                #Set d1 and d2 to first two points of the triangle
                d1 = polygon1.getPoint(i11)
                i12 = (i11 + 1) % (polygon1.getNumPoints())
                d2 = polygon1.getPoint(i12)

                isdiagonal = False;
                #for every second triangle
                for polygon2 in self.polygons:
                    if polygon1 == polygon2:
                        continue

                    #If the two triangles share two neighbouring points, isdiagonal is true
                    #so if i11 = i22 and i12 = i21
                    for i21 in range(polygon2.getNumPoints()):
                        if (d2.x != polygon2.getPoint(i21).x) or (d2.y != polygon2.getPoint(i21).y):
                            continue
          
                        i22 = (i21 + 1) % (polygon2.getNumPoints());
                        if (d1.x != polygon2.getPoint(i22).x) or (d1.y != polygon2.getPoint(i22).y):
                            continue
        
                        isdiagonal = True
                        break
        
                    if isdiagonal:
                        break
            
                #if the triangles have no diagonal, go to next triangle combination
                if not isdiagonal:
                    continue
      
                #Assign p1, p2, p3
                p2 = polygon1.getPoint(i11)

                if i11 == 0:
                    i13 = polygon1.getNumPoints() - 1
                else:
                    i13 = i11 - 1
                p1 = polygon1.getPoint(i13)

                if i22 == (polygon2.getNumPoints() - 1):
                    i23 = 0
                else:
                    i23 = i22 + 1
                p3 = polygon2.getPoint(i23)

                #Check if the angle is convex between i11/i22(diagonal vertex) and the vertices previous from i11 and next from i22
                if not self.isConvex(p1, p2, p3):
                    continue

                #Assign p1, p2, p3
                p2 = polygon1.getPoint(i12)

                if i12 == (polygon1.getNumPoints() - 1):
                    i13 = 0
                else:
                    i13 = i12 + 1
                p3 = polygon1.getPoint(i13)

                if (i21 == 0):
                    i23 = polygon2.getNumPoints() - 1
                else:
                    i23 = i21 - 1
                p1 = polygon2.getPoint(i23)

                #Check if the angle is convex between i12/i21(diagonal vertex) and the vertices previous from i23 and next from i12
                if not self.isConvex(p1, p2, p3):
                    continue;
      
                #Now both angles are convex, so removing the diagonal gives a convex polygon
                #Create new polygon with vertices from poly1 + poly2 without i12 and i11, which are doubles
                newPolygon = Polygon([],[])
                #Add points from polygon1 except i11
                j = i12
                while j != i11:
                    newPolygon.v.append(polygon1.getPoint(j))
                    j = (j + 1) % (polygon1.getNumPoints())

                #Add points from polygon2 except i21
                j = i22
                while j != i21:
                    newPolygon.v.append(polygon2.getPoint(j))
                    j = (j + 1) % (polygon2.getNumPoints())

                #replace poly1 and poly2 with newpoly
                self.polygons = [newPolygon if p == polygon1 else p for p in self.polygons]
                self.polygons.remove(polygon2);
                
                i11 = -1;

                continue

            #If no new polygon was created, move on to the next one
            t1 += 1

        print(len(self.polygons), 'polygons')
        self.DT.polygons = self.polygons
        return self

    def plot(self):
        """
        Plot the triangulation
        """
        allPoints = []
        allPolygons = []
        for polygon in self.polygons:
            polygonPoints = []
            for vertex in polygon.v:
                allPoints.append(vertex)
                polygonPoints.append(vertex)
            polygonPoints.append(polygonPoints[0])
            allPolygons.append(polygonPoints)

        x_s = [p.x for p in allPoints]
        y_s = [p.y for p in allPoints]

        #for t in self.triangulation:
        #    ts.append((ps.index(t.v[0]), ps.index(t.v[1]), ps.index(t.v[2])))

        fig, ax = plt.subplots()
        ax.scatter(x_s, y_s)
        for polygon in allPolygons:
            x_p = [p.x for p in polygon]
            y_p = [p.y for p in polygon]
            ax.plot(x_p, y_p, 'b')
        #ax.triplot(tri.Triangulation(x_s, y_s, ts), 'bo--')
        ax.set_title('Plot of polygons')

        plt.show()

    def export(self):
        export = {
            "type": "CGSHOP2023_Solution",
            "instance": self.DT.name,
            "polygons": []
        }

        for polygon in self.polygons:
            export['polygons'].append([{'x': v.x, 'y': v.y} for v in polygon.v])

        # Serializing json
        json_object = json.dumps(export, indent=4)

        # Writing to sample.json
        with open("hm-" + self.DT.name + "-sol" + ".json", "w") as outfile:
            outfile.write(json_object)
