from OpenGL.GL import *
from glfw.GLFW import *

from variables import global_cam, node_manager

def key_callback(window, key, scancode, action, mods):
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else:
        if action==GLFW_PRESS or action==GLFW_REPEAT:
            if key==GLFW_KEY_V:
                global_cam.toggle_projection()
            elif key == GLFW_KEY_H:
                node_manager.toggle_render_mode()
            elif key == GLFW_KEY_Z:
                node_manager.toggle_frame_mode()
                

