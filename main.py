# region Imports
import glfw
import moderngl

from graphics import *
from input import *
import glm
#endregion

# region GLobal Variables
global window

defaultShader: moderngl.Program
defaultShaderCameraUniform: moderngl.Uniform
quadMesh: Mesh

lastFrameTime: float
deltaTime: float

screenDim = (640, 480)

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


def Update():
    global deltaTime, lastFrameTime
    deltaTime = glfw.get_time() - lastFrameTime

    # Render here, e.g. using pyOpenGL
    ctx.clear(0.05, 0.1, 0.2)
    for key in keys:
        key.Update(window)
    
    if escapeKey.held:
        glfw.set_window_should_close(window, True)
    
    cameraMatrix = glm.identity(glm.mat4)
    cameraMatrix *= glm.scale(glm.vec3(screenDim[1] / screenDim[0], 1.0, 1.0))

    if spaceKey.held:
        defaultShaderCameraUniform.write(cameraMatrix)
        quadMesh.vao.render()

    # Should happen after most if not all frame logic
    lastFrameTime = glfw.get_time()

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