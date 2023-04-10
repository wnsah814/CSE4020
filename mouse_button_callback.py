from OpenGL.GL import *
import glfw

from variables import drag
def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            print("Left mouse button pressed")
            xpos, ypos = glfw.get_cursor_pos(window)
            drag.set_position(xpos, ypos)
        elif action == glfw.RELEASE:
            print("Left mouse button released")
            
    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            print("Right mouse button pressed")
            xpos, ypos = glfw.get_cursor_pos(window)
            drag.set_position(xpos, ypos)
        elif action == glfw.RELEASE:
            print("Right mouse button released")