import sys
import sdl2.ext

def Main():
    print("Greetings universe and awesomers!\n")

    sdl2.ext.init()

    window = sdl2.ext.Window("Hello World!", size=(640, 480))
    window.show()

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    spriterenderer = factory.create_sprite_render_system(window)

    while True:
        pass

    print("Farewell universe!\n")

Main()