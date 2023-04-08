from OpenGL.GL import *
import glfw
from variables import drag, global_cam
import numpy as np
import glm

def cursor_position_callback(window, xpos, ypos):
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
        print("Orbit")
        drag_start_x, drag_start_y = drag.get_position()
        # dx, dy = xpos - drag_start_x, ypos - drag_start_y
        dx, dy = xpos - drag_start_x, drag_start_y - ypos 
        print(f"dx: {dx}, dy: {dy}")
        drag.set_position(xpos, ypos)

        SCALER = 0.1
        # SCALER = 0.01

        # if not dx == 0:
        #     global_cam.add_azi(np.radians(dx * SCALER))
        if not dy == 0:
            global_cam.add_ele(dy * SCALER)
            # global_cam.add_ele(np.radians(dy * SCALER))
        global_cam.up = glm.vec3(0, -1, 0) if np.sin(global_cam.elevation) < 0 else glm.vec3(0, 1, 0)
                    
    elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
        print("Pan")

        drag_start_x, drag_start_y = drag.get_position()

        dx, dy = xpos - drag_start_x, drag_start_y - ypos
        
        print(xpos, ypos, drag_start_x, drag_start_y, dx, dy)
        
        print(f"dx: {dx}, dy: {dy}")
        drag.set_position(xpos, ypos)

        SCALER = 0.005
        global_cam.pan += glm.vec3(SCALER * dx * np.cos(-global_cam.azimuth),SCALER * dy, SCALER * dx * np.sin(-global_cam.azimuth))
        print(global_cam.pan)
        print()