from OpenGL.GL import *
from glfw.GLFW import *
from variables import global_cam, joint_manager

def key_callback(window, key, scancode, action, mods):
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else:
        if action==GLFW_PRESS or action==GLFW_REPEAT:
            if key==GLFW_KEY_V:
                global_cam.toggle_projection()
            elif key == GLFW_KEY_1:
                joint_manager.boxmode = False
            elif key == GLFW_KEY_2:
                joint_manager.boxmode = True
            elif key == GLFW_KEY_SPACE:
                joint_manager.animate = not joint_manager.animate;
                joint_manager.oldtime = glfwGetTime()
                joint_manager.frow = 0
                joint_manager.fcol = 0
                

