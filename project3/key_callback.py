from OpenGL.GL import *
from glfw.GLFW import *

from variables import global_cam

def key_callback(window, key, scancode, action, mods):
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else:
        if action==GLFW_PRESS or action==GLFW_REPEAT:
            if key==GLFW_KEY_V:
                global_cam.toggle_projection()
            elif key == GLFW_KEY_1:
                1
                # node_manager.toggle_render_mode()
            elif key == GLFW_KEY_2:
                1
                # node_manager.toggle_frame_mode()
            elif key == GLFW_KEY_SPACE:
                1
                # node_manager.toggle_frame_mode()
                

