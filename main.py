# region Imports
import glfw
import moderngl

from graphics import *
from input import *
import glm
#endregion

# region GLobal Variables
global window

lastFrameTime: float
deltaTime: float

screenDim: tuple[int, int] = (640, 480)

camPos: glm.vec2 = glm.vec2(0)
camZoom: float = 10.0
camSpeed: float = 10.0

# endregion

def FramebufferSizeCallback(window, width: int, height: int):
    global screenDim
    screenDim = (width, height)
    ctx.viewport = (0, 0, width, height)

def Start():
    global window, lastFrameTime, ctx, defaultShader, defaultShaderCameraUniform, quadMesh
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
    ctx = moderngl.get_context()

    glfw.set_framebuffer_size_callback(window, FramebufferSizeCallback)


    defaultShader = OpenShader("Resources/Shaders/DefaultShaderVert.glsl", "Resources/Shaders/DefaultShaderFrag.glsl", ctx)
    defaultShaderCameraUniform = defaultShader["camera"]
    quadMesh = Mesh("Resources/Meshes/Quad.txt", defaultShader, ctx)

    lastFrameTime = glfw.get_time()
    
    testTexture = OpenTexture("Resources/Sprites/TestSprite.png", ctx)


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

    defaultShaderCameraUniform.write(cameraMatrix)
    quadMesh.vao.render()


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