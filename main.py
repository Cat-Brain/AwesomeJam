# region Imports
import glfw
import moderngl

from graphics import *
from input import *
#endregion

# region GLobal Variables
global window

defaultShader: moderngl.Program
quadMesh: Mesh

lastFrameTime: float
deltaTime: float

# endregion

def Start():
    global window, lastFrameTime, ctx, defaultShader, quadMesh
    # Initialize the library
    if not glfw.init():
        return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    ctx = moderngl.get_context()

    lastFrameTime = glfw.get_time()


    defaultShader = OpenShader("Resources/Shaders/DefaultShaderVert.glsl", "Resources/Shaders/DefaultShaderFrag.glsl", ctx)
    quadMesh = Mesh("Resources/Meshes/Quad.txt", defaultShader, ctx)


def Update():
    global deltaTime, lastFrameTime
    deltaTime = glfw.get_time() - lastFrameTime

    # Render here, e.g. using pyOpenGL
    ctx.clear(0.05, 0.1, 0.2)
    for key in keys:
        key.Update(window)
    
    if escapeKey.held:
        glfw.set_window_should_close(window, True)
    
    if spaceKey.held:
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