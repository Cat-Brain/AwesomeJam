# region Imports

import glfw
import moderngl
import glm
from PIL import Image
from PIL import ImageOps
import numpy as np

#endregion

#region Classes

class Key:
    pressed: bool = False
    held: bool = False
    released: bool = False
    keycode: int
    isMouse: bool

    def __init__(self, keycode: int, isMouse: bool = False):
        self.keycode = keycode
        self.isMouse = isMouse
        global keys
        keys.append(self)        

    def Update(self, window):
        now_held = glfw.get_mouse_button(window, self.keycode) if self.isMouse else glfw.get_key(window, self.keycode)
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
        self.texture = ctx.texture([file.width, file.height], 4, ImageOps.flip(file).tobytes())
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

    def Draw(self, location: int = 0):
        spriteShaderCameraUniform.write(camMatrix)
        self.texture.Use(location)
        spriteShaderTextureUniform.value = location
        spriteShaderPosScaleUniform.write(glm.vec4(self.pos, self.scale))
        quadMesh.Draw()

#endregion

# region GLobal Variables
global window

ctx: moderngl.Context

framebuffer: moderngl.Framebuffer

lastFrameTime: float
deltaTime: float

screenDim: glm.ivec2 = glm.ivec2(512, 480)
framebufferDim: tuple[int, int] = (256, 240)

rawCursorPos: glm.ivec2 = glm.ivec2(0)
localCursorPos: glm.vec2 = glm.vec2(0)
cursorPos: glm.vec2 = glm.vec2(0)

camPos: glm.vec2 = glm.vec2(0)
camZoom: float = 10.0
camSpeed: float = 10.0
camMatrix: glm.mat4

spriteShader: moderngl.Program
spriteShaderCameraUniform: moderngl.Uniform
spriteShaderTextureUniform: moderngl.Uniform
spriteShaderPosScaleUniform: moderngl.Uniform

backgroundShader: moderngl.Program
backgroundShaderCameraUniform: moderngl.Uniform
backgroundShaderFrequencyUniform: moderngl.Uniform
backgroundShaderColorsUniform: moderngl.Uniform
backgroundShaderTimeUniform: moderngl.Uniform

backgroundFrequency: float = 0.05
backgroundTimeFrequency: float = 0.003

quadMesh: Mesh
backgroundQuadMesh: Mesh

testTexture: Texture
testTexture2: Texture

testSprite: Sprite
testSprite2: Sprite

# Must be defined before all keys are
keys = []
escapeKey = Key(glfw.KEY_ESCAPE)
spaceKey = Key(glfw.KEY_SPACE)
aKey = Key(glfw.KEY_A)
dKey = Key(glfw.KEY_D)
sKey = Key(glfw.KEY_S)
wKey = Key(glfw.KEY_W)
mouseLeftClick = Key(glfw.MOUSE_BUTTON_LEFT, True)
mouseRightClick = Key(glfw.MOUSE_BUTTON_RIGHT, True)

# endregion

#region Functions

def NearestFramebufferViewport(width: int, height: int):
    return (0, 0, width, height)
    ratio: int = np.ceil(height / framebufferDim[1])
    return (0, 0, np.ceil(width * ratio), np.ceil())

def FramebufferSizeCallback(window, width: int, height: int):
    global screenDim
    screenDim = glm.vec2(width, height)
    ctx.viewport = (0, 0, width, height)
    framebuffer.viewport = NearestFramebufferViewport(width, height)


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
    global window, ctx, framebuffer, lastFrameTime, spriteShader, spriteShaderCameraUniform, spriteShaderTextureUniform, spriteShaderPosScaleUniform
    global backgroundShader, backgroundShaderCameraUniform, backgroundShaderFrequencyUniform, backgroundShaderColorsUniform, backgroundShaderTimeUniform
    global quadMesh, backgroundQuadMesh, testTexture, testTexture2, testSprite, testSprite2
    # Initialize the library
    if not glfw.init():
        return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(screenDim.x, screenDim.y, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    ctx = moderngl.create_context()

    glfw.set_framebuffer_size_callback(window, FramebufferSizeCallback)

    framebuffer = ctx.simple_framebuffer((256, 240))

    spriteShader = OpenShader("Resources/Shaders/DefaultShaderVert.glsl", "Resources/Shaders/DefaultShaderFrag.glsl")
    spriteShaderCameraUniform = spriteShader["camera"]
    spriteShaderTextureUniform = spriteShader["tex"]
    spriteShaderPosScaleUniform = spriteShader["posScale"]
    
    backgroundShader = OpenShader("Resources/Shaders/BackgroundShaderVert.glsl", "Resources/Shaders/BackgroundShaderFrag.glsl")
    backgroundShaderCameraUniform = backgroundShader["camera"]
    backgroundShaderFrequencyUniform = backgroundShader["frequency"]
    backgroundShaderColorsUniform = backgroundShader["colors"]
    backgroundShaderTimeUniform = backgroundShader["time"]

    quadMesh = Mesh("Resources/Meshes/Quad.txt", spriteShader)
    backgroundQuadMesh = Mesh("Resources/Meshes/Quad.txt", backgroundShader)

    lastFrameTime = glfw.get_time()
    
    testTexture = Texture(Image.open("Resources/Sprites/TestSprite.png"))
    testTexture2 = Texture(Image.open("Resources/Sprites/TestSprite2.png"))

    testSprite = Sprite(testTexture)
    testSprite2 = Sprite(testTexture)


def Update():
    global deltaTime, lastFrameTime, camPos, camMatrix, rawCursorPos, localCursorPos, cursorPos
    deltaTime = glfw.get_time() - lastFrameTime
    lastFrameTime = glfw.get_time()

    ctx.clear(0.05, 0.1, 0.2)
    for key in keys:
        key.Update(window)

    tempCursorPos = glfw.get_cursor_pos(window)
    rawCursorPos = glm.ivec2(tempCursorPos[0], tempCursorPos[1])
    localCursorPos = glm.vec2(rawCursorPos.x * 2 / screenDim.x - 1, 1.0 - rawCursorPos.y * 2 / screenDim.y)

    
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
    
    camMatrix = glm.identity(glm.mat4)
    camMatrix *= glm.scale(glm.vec3(screenDim[1] / (screenDim[0] * camZoom), 1.0 / camZoom, 1.0))
    camMatrix *= glm.translate(glm.vec3(-camPos, 0))
    invCamMatrix = glm.inverse(camMatrix)

    cursorPos = glm.vec2(invCamMatrix * glm.vec4(localCursorPos, 0, 0)) + camPos

    backgroundShaderCameraUniform.write(invCamMatrix)
    backgroundShaderFrequencyUniform.write(glm.vec2(backgroundFrequency, backgroundTimeFrequency))
    backgroundShaderColorsUniform.write(b''.join([glm.vec4(0.18, 0.19, 0.52, 0.75), glm.vec4(0.16, 0.13, 0.45, 0.5), glm.vec4(0.13, 0.06, 0.34, 0.25)]))
    backgroundShaderTimeUniform.value = lastFrameTime
    backgroundQuadMesh.Draw()


    testSprite.Draw()
    testSprite2.pos = cursorPos
    testSprite2.texture = testTexture if mouseLeftClick.held else testTexture2
    testSprite2.Draw()


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