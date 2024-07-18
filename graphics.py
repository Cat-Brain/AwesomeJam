from OpenGL.GL import *
from mathLib import *

class Mesh:
    vao: int
    vbo: int
    ebo: int
    vertices: list[Vec2f]
    indices: list[(int, int, int)]

    def __init__(self, location: str):
        file = open(location, "r")
        data: str = file.read()
        file.close()

        splitData = data.split("\n\n")
        if len(splitData) != 2:
            print(f"ERROR:\nMesh at location {location} had {"less" if len(splitData) < 2 else "more"} than 2 blocks of data!")
            return
        
        self.vertices = list()
        for vertStr in splitData[0].split("\n"):
            splitVert = vertStr.split(" ")
            if (len(splitVert) != 2):
                print(f"ERROR:\nMesh at location {location} had a vertex which was ({vertStr}) with {"less" if len(splitData) < 2 else "more"} than 2 points of data!")
                return
            try:
                self.vertices.append(Vec2f(float(splitVert[0]), float(splitVert[1])))
            except:
                print(f"ERROR:\nMesh at location {location} had a vertex which was ({vertStr}) with a non-float value!")
                return
        
        self.indices = list()
        for indStr in splitData[1].split("\n"):
            splitInd = indStr.split(" ")
            if (len(splitInd) != 3):
                print(f"ERROR:\nMesh at location {location} had an index group which was ({indStr}) with {"less" if len(splitData) < 3 else "more"} than 3 points of data!")
                return
            try:
                self.indices.append((int(splitInd[0]), int(splitInd[1]), int(splitInd[2])))
            except:
                print(f"ERROR:\nMesh at location {location} had an index group which was ({indStr}) with a non-int value!")
                return
        
        for vert in self.vertices:
            print(vert)
        print("")
        for tri in self.indices:
            print(tri)