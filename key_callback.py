from OpenGL.GL import *
from glfw.GLFW import *
import numpy as np

from variables import global_cam

def key_callback(window, key, scancode, action, mods):
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else:
        if action==GLFW_PRESS or action==GLFW_REPEAT:
            if key==GLFW_KEY_1:
                global_cam.add_azi(np.radians(-10))
            elif key==GLFW_KEY_3:
                global_cam.add_azi(np.radians(10))
            # elif key==GLFW_KEY_2:
            #     global_cam.add_height(0.025)
            # elif key==GLFW_KEY_W:
            #     global_cam.add_height(-0.025)
            elif key==GLFW_KEY_V:
                global_cam.toggle_projection()
            elif key==GLFW_KEY_0:
                global_cam.reset()
