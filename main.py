# region Imports

import glfw
import moderngl
import glm
from PIL import Image
from PIL import ImageOps
import numpy as np
from enum import Enum

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

    def __init__(self, location: str):
        file = open(MESH_PATH + location, "r")
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


class Shader:
    program: moderngl.Program
    vertPath: str
    fragPath: str

    def __init__(self, vertPath: str, fragPath: str):
        self.vertPath = vertPath
        self.fragPath = fragPath
        shaders.append(self)

    def Open(self):
        file = open(SHADER_PATH + self.vertPath)
        vertShader = file.read()
        file.close()
        file = open(SHADER_PATH + self.fragPath)
        fragShader = file.read()
        file.close()
        self.program = ctx.program(vertShader, fragShader)


class Texture:
    path: str
    texture: moderngl.Texture
    sampler: moderngl.Sampler

    def __init__(self, path: str):
        self.path = path
        textures.append(self)

    def Open(self):
        file = Image.open(SPRITE_PATH + self.path)
        self.texture = ctx.texture([file.width, file.height], 4, ImageOps.flip(file).tobytes())
        self.sampler = ctx.sampler(texture=self.texture)
        self.sampler.filter = (moderngl.NEAREST, moderngl.NEAREST)


    def Use(self, location=0):
        self.sampler.use(location)


class Sprite:
    texture: Texture
    pos: glm.vec2
    scale: glm.vec2

    def __init__(self, texture: Texture, pos: glm.vec2 = glm.vec2(0), scale: glm.vec2 = glm.vec2(1)):
        self.texture = texture
        self.pos = pos
        self.scale = scale

    def Draw(self, location: int = 0):
        spriteShaderCameraUniform.write(camMatrix)
        self.texture.Use(location)
        spriteShaderTextureUniform.value = location
        spriteShaderPosScaleUniform.write(glm.vec4(ToGrid(self.pos), self.scale * 0.5))
        spriteVAO.render()


class ButtonState(Enum):
    DEFAULT = 0
    HOVERED = 1
    HELD = 2

class Button(Sprite):
    defaultTexture: Texture
    hoveredTexture: Texture
    heldTexture: Texture
    triggeredOnRelease: bool

    def __init__(self, defaultTexture: Texture, hoveredTexture: Texture, heldTexture: Texture, pos: glm.vec2 = glm.vec2(0), scale: glm.vec2 = glm.vec2(1), triggeredOnRelease: bool = True):
        self.defaultTexture = defaultTexture
        self.hoveredTexture = hoveredTexture
        self.heldTexture = heldTexture
        self.triggeredOnRelease = triggeredOnRelease
        Sprite.__init__(self, defaultTexture, pos, scale)
    
    def State(self) -> ButtonState:
        gridPos = ToGrid(self.pos)
        minPos = gridPos - self.scale * 0.5
        maxPos = gridPos + self.scale * 0.5
        gridCursor = ToGrid(cursorPos)
        isHovered = gridCursor.x >= minPos.x and gridCursor.y >= minPos.y and gridCursor.x <= maxPos.x and gridCursor.y <= maxPos.y
        if isHovered:
            return ButtonState.HELD if mouseLeftClick.held else ButtonState.HOVERED
        else:
            return ButtonState.DEFAULT

    def Update(self):
        if self.State() != ButtonState.DEFAULT and ((mouseLeftClick.released and self.triggeredOnRelease) or (mouseLeftClick.pressed and not self.triggeredOnRelease)):
            self.Activate()
    
    def Activate(self):
        print("Activate!")
    
    def Draw(self, location: int = 0):
        match self.State():
            case ButtonState.DEFAULT:
                self.texture = self.defaultTexture
            case ButtonState.HOVERED:
                self.texture = self.hoveredTexture
            case ButtonState.HELD:
                self.texture = self.heldTexture
        Sprite.Draw(self, location)

#endregion

# region GLobal Variables
global window

ctx: moderngl.Context

framebuffer: moderngl.Framebuffer

lastFrameTime: float
deltaTime: float

screenDim: glm.ivec2 = glm.ivec2(512, 480)

WINDOW_NAME = "Awesome Jam! =]"

V_SYNC = True
DISPLAY_FPS = True

framesThisSecond: int = 0

rawCursorPos: glm.ivec2 = glm.ivec2(0)
localCursorPos: glm.vec2 = glm.vec2(0)
cursorPos: glm.vec2 = glm.vec2(0)
gridCursorPos: glm.vec2 = glm.vec2(0)

camPos: glm.vec2 = glm.vec2(0)
camSpeed: float = 10.0
camMatrix: glm.mat4

AUDIO_PATH: str = "Resources/Audio/"
MESH_PATH: str = "Resources/Meshes/"
SHADER_PATH: str = "Resources/Shaders/"
SPRITE_PATH: str = "Resources/Sprites/"

PIXELS_PER_UNIT: int = 16
CAMERA_ZOOM: int = 10
FRAMEBUFFER_HEIGHT: int = PIXELS_PER_UNIT * CAMERA_ZOOM * 2

shaders: list[Shader] = []

spriteShader: Shader = Shader("SpriteShaderVert.glsl", "SpriteShaderFrag.glsl")
spriteShaderCameraUniform: moderngl.Uniform
spriteShaderTextureUniform: moderngl.Uniform
spriteShaderPosScaleUniform: moderngl.Uniform

backgroundShader: Shader = Shader("BackgroundShaderVert.glsl", "BackgroundShaderFrag.glsl")
backgroundShaderMinMaxUniform: moderngl.Uniform
backgroundShaderFrequencyUniform: moderngl.Uniform
backgroundShaderColorsUniform: moderngl.Uniform
backgroundShaderTimeUniform: moderngl.Uniform
backgroundShaderStippleUniform: moderngl.Uniform
backgroundShaderStippleOffsetUniform: moderngl.Uniform # PPU stands for Pixels Per Unit

BACKGROUND_FREQUENCY: float = 0.05
BACKGROUND_TIME_FREQUENCY: float = 0.003
BACKGROUND_STIPPLE_DIST: float = 0.005

toScreenShader: Shader = Shader("ToScreenVert.glsl", "ToScreenFrag.glsl")
toScreenTextureUniform: moderngl.Uniform
toScreenStretchUniform: moderngl.Uniform

quadMesh: Mesh
spriteVAO: moderngl.VertexArray
backgroundVAO: moderngl.VertexArray
toScreenVAO: moderngl.VertexArray

textures: list[Texture] = []

testTexture: Texture = Texture("TestSprite.png")
testTexture2: Texture = Texture("TestSprite2.png")
testTexture3: Texture = Texture("TestSprite3.png")

testSprite: Sprite
testButton: Button

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

def ToGrid(value: glm.vec2):
    return glm.round(value * PIXELS_PER_UNIT) / PIXELS_PER_UNIT

def NearestFramebufferViewport():
    ratio: int = np.ceil(screenDim[1] / FRAMEBUFFER_HEIGHT)
    return (int(np.ceil(screenDim[0] / ratio)), int(np.ceil(screenDim[1] / ratio)))

def GetFramebufferStretch():
    ratio: int = np.ceil(screenDim[1] / FRAMEBUFFER_HEIGHT)
    return glm.vec2(1 / (ratio * framebuffer.width / screenDim[0]), 1 / (ratio * framebuffer.height / screenDim[1]))

def FramebufferSizeCallback(window, width: int, height: int):
    global screenDim, framebuffer
    screenDim = glm.ivec2(width, height)
    ctx.viewport = (0, 0, width, height)
    framebuffer.release()
    framebuffer = ctx.framebuffer(ctx.texture(NearestFramebufferViewport(), 4))


def OpenShader(vertLocation: str, fragLocation: str) -> moderngl.Program:
    file = open(SHADER_PATH + vertLocation)
    vertShader = file.read()
    file.close()
    file = open(SHADER_PATH + fragLocation)
    fragShader = file.read()
    file.close()
    return ctx.program(vertShader, fragShader)

#endregion

def Start():
    global window, ctx, framebuffer, lastFrameTime
    global spriteShader, spriteShaderCameraUniform, spriteShaderTextureUniform, spriteShaderPosScaleUniform
    global backgroundShader, backgroundShaderMinMaxUniform, backgroundShaderFrequencyUniform, backgroundShaderColorsUniform
    global backgroundShaderTimeUniform, backgroundShaderStippleUniform, backgroundShaderStippleOffsetUniform
    global toScreenShader, toScreenTextureUniform, toScreenStretchUniform
    global quadMesh, spriteVAO, backgroundVAO, toScreenVAO, testTexture, testTexture2, testTexture3, testSprite, testButton
    # Initialize the library
    if not glfw.init():
        return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(screenDim.x, screenDim.y, WINDOW_NAME, None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    ctx = moderngl.create_context()
    framebuffer = ctx.simple_framebuffer([FRAMEBUFFER_HEIGHT, FRAMEBUFFER_HEIGHT])

    glfw.set_framebuffer_size_callback(window, FramebufferSizeCallback)
    FramebufferSizeCallback(window, screenDim[0], screenDim[1])


    for shader in shaders:
        shader.Open()

    spriteShaderCameraUniform = spriteShader.program["camera"]
    spriteShaderTextureUniform = spriteShader.program["tex"]
    spriteShaderPosScaleUniform = spriteShader.program["posScale"]
    
    backgroundShaderMinMaxUniform = backgroundShader.program["minMaxPos"]
    backgroundShaderFrequencyUniform = backgroundShader.program["frequency"]
    backgroundShaderColorsUniform = backgroundShader.program["colors"]
    backgroundShaderTimeUniform = backgroundShader.program["time"]
    backgroundShaderStippleUniform = backgroundShader.program["stippleDist"]
    backgroundShaderStippleOffsetUniform = backgroundShader.program["stippleOffset"]

    toScreenTextureUniform = toScreenShader.program["tex"]
    toScreenStretchUniform = toScreenShader.program["stretch"]

    quadMesh = Mesh("Quad.txt")
    spriteVAO = ctx.vertex_array(spriteShader.program, quadMesh.vbo, "aPos", "aUV", index_buffer=quadMesh.ebo)
    backgroundVAO = ctx.vertex_array(backgroundShader.program, quadMesh.vbo, "aPos", "aUV", index_buffer=quadMesh.ebo)
    toScreenVAO = ctx.vertex_array(toScreenShader.program, quadMesh.vbo, "aPos", "aUV", index_buffer=quadMesh.ebo)

    lastFrameTime = glfw.get_time()
    
    for texture in textures:
        texture.Open()

    testSprite = Sprite(testTexture)
    testButton = Button(testTexture, testTexture2, testTexture3, glm.vec2(3, 0))


def Update():
    global deltaTime, lastFrameTime, framesThisSecond, camPos, gridCamPos, camMatrix, rawCursorPos, localCursorPos, cursorPos, BACKGROUND_STIPPLE_DIST
    glfw.swap_interval(1 if V_SYNC else 0)
    if DISPLAY_FPS:
        framesThisSecond += 1
        if int(glfw.get_time()) != int(lastFrameTime):
            glfw.set_window_title(window, f"{WINDOW_NAME} FPS = {framesThisSecond}")
            framesThisSecond = 0
    else:
        glfw.set_window_title(window, WINDOW_NAME)
    

    deltaTime = glfw.get_time() - lastFrameTime
    lastFrameTime = glfw.get_time()


    framebuffer.use()
    framebuffer.clear(0.05, 0.1, 0.2)

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
    gridCamPos = ToGrid(camPos)


    testButton.Update()

    
    camMatrix = glm.identity(glm.mat4)
    camMatrix *= glm.scale(glm.vec3(PIXELS_PER_UNIT * 2 / framebuffer.width, PIXELS_PER_UNIT * 2 / framebuffer.height, 1.0))
    camMatrix *= glm.translate(glm.vec3(-gridCamPos, 0))
    invCamMatrix = glm.inverse(camMatrix)

    cursorPos = glm.vec2(invCamMatrix * glm.vec4(localCursorPos, 0, 0)) + camPos

    framebufferDim: glm.vec2 = glm.vec2(framebuffer.width, framebuffer.height)
    minCamPos: glm.vec2 = gridCamPos - framebufferDim * 0.5 / PIXELS_PER_UNIT
    maxCamPos: glm.vec2 = gridCamPos + framebufferDim * 0.5 / PIXELS_PER_UNIT
    backgroundShaderMinMaxUniform.write(glm.vec4(minCamPos.x, minCamPos.y, maxCamPos.x, maxCamPos.y))
    backgroundShaderFrequencyUniform.write(glm.vec2(BACKGROUND_FREQUENCY, BACKGROUND_TIME_FREQUENCY))
    backgroundShaderColorsUniform.write(b''.join([glm.vec4(0.18, 0.19, 0.52, 0.75), glm.vec4(0.16, 0.13, 0.45, 0.5), glm.vec4(0.13, 0.06, 0.34, 0.25)]))
    backgroundShaderTimeUniform.value = lastFrameTime
    backgroundShaderStippleUniform.value = BACKGROUND_STIPPLE_DIST
    backgroundShaderStippleOffsetUniform.value = int((gridCamPos.x + gridCamPos.y) * PIXELS_PER_UNIT) % 2
    backgroundVAO.render()


    testSprite.Draw()
    testButton.Draw()

    ctx.screen.use()

    framebuffer.color_attachments[0].use(0)
    toScreenTextureUniform.value = 0
    toScreenStretchUniform.write(GetFramebufferStretch())
    toScreenVAO.render()


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