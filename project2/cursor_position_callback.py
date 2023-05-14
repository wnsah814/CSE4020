from OpenGL.GL import *
import glfw
from variables import drag, global_cam
import glm

def cursor_position_callback(window, xpos, ypos):
    # orbit
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
        drag_start_x, drag_start_y = drag.get_position()
        dx, dy = drag_start_x - xpos , drag_start_y - ypos
        drag.set_position(xpos, ypos)

        SCALER = 0.1

        if not dx == 0:
            global_cam.add_azi(glm.radians(dx * SCALER))
                
        if not dy == 0:
            global_cam.add_ele(glm.radians(dy * SCALER))
        global_cam.up = glm.vec3(0, -1, 0) if glm.sin(global_cam.elevation) < 0 else glm.vec3(0, 1, 0)
        
    # pan
    elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
        drag_start_x, drag_start_y = drag.get_position()
        dx, dy = drag_start_x - xpos , drag_start_y - ypos
        drag.set_position(xpos, ypos)
        V = global_cam.get_view_matrix()
        V = glm.inverse(V)
        if not dx == 0:
            global_cam.pan += V[0].xyz * 0.01 * dx
        if not dy == 0:
            global_cam.pan -= V[1].xyz * 0.01 * dy