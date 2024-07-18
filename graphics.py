from OpenGL.GL import *
from mathLib import *
from array import array
import numpy as np
from sys import getsizeof

class Mesh:
    vao: int
    vbo: int
    ebo: int
    vertices: array
    indices: array

    def __init__(self, location: str):
        file = open(location, "r")
        data: str = file.read()
        file.close()

        splitData = data.split("\n\n")
        if len(splitData) != 2:
            print(f"ERROR:\nMesh at location {location} had {"less" if len(splitData) < 2 else "more"} than 2 blocks of data!")
            return
        
        splitVert = splitData[0].split("\n")
        self.vertices = array("f", [0.0] * len(splitVert) * 2)
        
        for i, vertStr in enumerate(splitVert):
            splitVert = vertStr.split(" ")
            if (len(splitVert) != 2):
                print(f"ERROR:\nMesh at location {location} had a vertex which was ({vertStr}) with {"less" if len(splitData) < 2 else "more"} than 2 points of data!")
                return
            try:
                self.vertices[i * 2] = float(splitVert[0])
                self.vertices[i * 2 + 1] = float(splitVert[1])
            except:
                print(f"ERROR:\nMesh at location {location} had a vertex which was ({vertStr}) with a non-float value!")
                return
        
        splitInd = splitData[1].split("\n")
        self.indices = array("I", [0] * len(splitInd) * 3)
        for i, indStr in enumerate(splitInd):
            splitInd = indStr.split(" ")
            if (len(splitInd) != 3):
                print(f"ERROR:\nMesh at location {location} had an index group which was ({indStr}) with {"less" if len(splitData) < 3 else "more"} than 3 points of data!")
                return
            try:
                self.indices[i * 3] = int(splitInd[0])
                self.indices[i * 3 + 1] = int(splitInd[1])
                self.indices[i * 3 + 2] = int(splitInd[2])
            except:
                print(f"ERROR:\nMesh at location {location} had an index group which was ({indStr}) with a non-int value!")
                return
            
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        #glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * self.vertices.itemsize, self.vertices., GL_STATIC_DRAW)
        #glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.indices) * self.vertices.itemsize, self.indices, GL_STATIC_DRAW);

        #glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*)0);
        #glEnableVertexAttribArray(0);

        glDeleteVertexArrays(1, self.vao)
        glDeleteBuffers(1, self.vbo)
        glDeleteBuffers(1, self.ebo)