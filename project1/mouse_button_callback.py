from OpenGL.GL import *
import glfw

from variables import drag
def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            xpos, ypos = glfw.get_cursor_pos(window)
            drag.set_position(xpos, ypos)
            
    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            xpos, ypos = glfw.get_cursor_pos(window)
            drag.set_position(xpos, ypos)