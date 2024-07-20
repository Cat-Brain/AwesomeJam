import glfw

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


# Must be defined before all keys are
keys = []
escapeKey = Key(glfw.KEY_ESCAPE)
spaceKey = Key(glfw.KEY_SPACE)
aKey = Key(glfw.KEY_A)
dKey = Key(glfw.KEY_D)
sKey = Key(glfw.KEY_S)
wKey = Key(glfw.KEY_W)