from OpenGL.GL import *
import glfw
from variables import drag, global_cam
import numpy as np
import glm

def cursor_position_callback(window, xpos, ypos):
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
        drag_start_x, drag_start_y = drag.get_position()
        dx, dy = xpos - drag_start_x, drag_start_y - ypos 
        drag.set_position(xpos, ypos)

        SCALER = 0.1

        if not dx == 0:
            global_cam.add_azi(glm.radians(dx * SCALER))
                
        if not dy == 0:
            global_cam.add_ele(glm.radians(dy * SCALER))
        global_cam.up = glm.vec3(0, -1, 0) if np.sin(global_cam.elevation) < 0 else glm.vec3(0, 1, 0)
                    
    elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
        drag_start_x, drag_start_y = drag.get_position()
        dx, dy = xpos - drag_start_x, drag_start_y - ypos
        drag.set_position(xpos, ypos)

        SCALER = 0.001
        global_cam.pan += glm.vec3(SCALER * dx * np.cos(-global_cam.azimuth), SCALER * dy, SCALER * dx * np.sin(-global_cam.azimuth)) * global_cam.distance