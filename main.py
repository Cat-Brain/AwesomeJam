# region Imports
import glfw
import moderngl
import glm
from PIL import Image
import numpy as np
#endregion

#region Classes

class Key:
    pressed: bool = False
    held: bool = False
    released: bool = False
    keycode: int

    def __init__(self, keycode: int):
        self.keycode = keycode
        global keys
        keys.append(self)        

    def Update(self, window):
        now_held = glfw.get_key(window, self.keycode)
        self.pressed = now_held and not self.held
        self.released = not now_held and self.held
        self.held = now_held


class Mesh:
    vao: moderngl.VertexArray
    vbo: moderngl.Buffer
    ebo: moderngl.Buffer
    vertices: np.ndarray
    indices: np.ndarray

    def __init__(self, location: str, shader: moderngl.Program):
        file = open(location, "r")
        data: str = file.read()
        file.close()

        splitData = data.split("\n\n")
        if len(splitData) != 2:
            print(f"ERROR:\nMesh at location {location} had {"less" if len(splitData) < 2 else "more"} than 2 blocks of data!")
            return
        
        splitVert = splitData[0].split("\n")
        self.vertices = np.empty(len(splitVert) * 4)
        
        for i, vertStr in enumerate(splitVert):
            splitVert = vertStr.split(" ")
            if (len(splitVert) != 4):
                print(f"ERROR:\nMesh at location {location} had a vertex which was ({vertStr}) with {"less" if len(splitData) < 4 else "more"} than 2 points of data!")
                return
            try:
                for j in range(4):
                    self.vertices[i * 4 + j] = float(splitVert[j])
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
        self.vao = ctx.vertex_array(shader, self.vbo, "aPos", "aUV", index_buffer=self.ebo)

    def Draw(self):
        self.vao.render()


class Texture:
    texture: moderngl.Texture
    sampler: moderngl.Sampler

    def __init__(self, file: Image.Image):
        self.texture = ctx.texture([file.width, file.height], 1, file.im)
        self.sampler = ctx.sampler(texture=self.texture)
        self.sampler.filter = (moderngl.NEAREST, moderngl.NEAREST)

    def Use(self, location=0):
        self.sampler.use(location)


class Sprite:
    texture: Texture
    pos: glm.vec2
    scale: glm.vec2

    def __init__(self, texture: moderngl.Sampler, pos: glm.vec2 = glm.vec2(0), scale: glm.vec2 = glm.vec2(1)):
        self.texture = texture
        self.pos = pos
        self.scale = scale

    def Draw(self, cameraMatrix: glm.mat4, location: int = 0):
        defaultShaderCameraUniform.write(cameraMatrix)
        self.texture.Use(location)
        defaultShaderTextureUniform.value = location
        defaultShaderPosScaleUniform.write(glm.vec4(self.pos, self.scale))
        quadMesh.Draw()

#endregion

# region GLobal Variables
global window

ctx: moderngl.Context

lastFrameTime: float
deltaTime: float

screenDim: tuple[int, int] = (640, 480)

camPos: glm.vec2 = glm.vec2(0)
camZoom: float = 10.0
camSpeed: float = 10.0

defaultShader: moderngl.Program
defaultShaderCameraUniform: moderngl.Uniform
defaultShaderTextureUniform: moderngl.Uniform
defaultShaderPosScaleUniform: moderngl.Uniform

quadMesh: Mesh

testTexture: Texture

testSprite: Sprite

# Must be defined before all keys are
keys = []
escapeKey = Key(glfw.KEY_ESCAPE)
spaceKey = Key(glfw.KEY_SPACE)
aKey = Key(glfw.KEY_A)
dKey = Key(glfw.KEY_D)
sKey = Key(glfw.KEY_S)
wKey = Key(glfw.KEY_W)

# endregion

#region Functions

def FramebufferSizeCallback(window, width: int, height: int):
    global screenDim
    screenDim = (width, height)
    ctx.viewport = (0, 0, width, height)


def OpenShader(vertLocation: str, fragLocation: str) -> moderngl.Program:
    file = open(vertLocation)
    vertShader = file.read()
    file.close()
    file = open(fragLocation)
    fragShader = file.read()
    file.close()
    return ctx.program(vertShader, fragShader)

#endregion

def Start():
    global ctx, window, lastFrameTime, defaultShader, defaultShaderCameraUniform, defaultShaderTextureUniform, defaultShaderPosScaleUniform, quadMesh, testTexture, testSampler, testSprite
    # Initialize the library
    if not glfw.init():
        return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(screenDim[0], screenDim[1], "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    ctx = moderngl.create_context()

    glfw.set_framebuffer_size_callback(window, FramebufferSizeCallback)

    defaultShader = OpenShader("Resources/Shaders/DefaultShaderVert.glsl", "Resources/Shaders/DefaultShaderFrag.glsl")
    defaultShaderCameraUniform = defaultShader["camera"]
    defaultShaderTextureUniform = defaultShader["tex"]
    defaultShaderPosScaleUniform = defaultShader["posScale"]

    quadMesh = Mesh("Resources/Meshes/Quad.txt", defaultShader)

    lastFrameTime = glfw.get_time()
    
    testTexture = Texture(Image.open("Resources/Sprites/TestSprite.png"))

    testSprite = Sprite(testTexture)


def Update():
    global deltaTime, lastFrameTime, camPos
    deltaTime = glfw.get_time() - lastFrameTime
    lastFrameTime = glfw.get_time()

    ctx.clear(0.05, 0.1, 0.2)
    for key in keys:
        key.Update(window)
    
    if escapeKey.held:
        glfw.set_window_should_close(window, True)

    camMovement = glm.vec2(0)
    if (aKey.held):
        camMovement.x -= 1
    if (dKey.held):
        camMovement.x += 1
    if (sKey.held):
        camMovement.y -= 1
    if (wKey.held):
        camMovement.y += 1
    if camMovement != glm.vec2(0):
        camPos += deltaTime * camSpeed * glm.normalize(camMovement)
    
    cameraMatrix = glm.identity(glm.mat4)
    cameraMatrix *= glm.scale(glm.vec3(screenDim[1] / (screenDim[0] * camZoom), 1.0 / camZoom, 1.0))
    cameraMatrix *= glm.translate(glm.vec3(-camPos, 0))

    testSprite.Draw(cameraMatrix)


    # Should happen after most if not all frame logic
    glfw.swap_buffers(window)
    glfw.poll_events()


def Close():
    glfw.terminate()


def Main():
    print("Greetings universe and awesomers!")

    Start()
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        Update()
    Close()

    print("Farewell universe!")

if __name__ == "__main__":
    Main()