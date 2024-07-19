import moderngl
import numpy as np

ctx: moderngl.Context

def OpenShader(vertLocation: str, fragLocation: str, ctx: moderngl.Context):
    file = open(vertLocation)
    vertShader = file.read()
    file.close()
    file = open(fragLocation)
    fragShader = file.read()
    file.close()
    return ctx.program(vertShader, fragShader)

class Mesh:
    vao: moderngl.VertexArray
    vbo: moderngl.Buffer
    ebo: moderngl.Buffer
    vertices: np.ndarray
    indices: np.ndarray

    def __init__(self, location: str, shader: moderngl.Program, ctx: moderngl.Context):
        file = open(location, "r")
        data: str = file.read()
        file.close()

        splitData = data.split("\n\n")
        if len(splitData) != 2:
            print(f"ERROR:\nMesh at location {location} had {"less" if len(splitData) < 2 else "more"} than 2 blocks of data!")
            return
        
        splitVert = splitData[0].split("\n")
        self.vertices = np.empty(len(splitVert) * 2)
        
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
        self.indices = np.empty(len(splitInd) * 3)
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
        
        self.vbo = ctx.buffer(self.vertices.astype('f4').tobytes())
        self.ebo = ctx.buffer(self.indices.astype('u4').tobytes())
        self.vao = ctx.vertex_array(shader, self.vbo, "aPos", index_buffer=self.ebo)