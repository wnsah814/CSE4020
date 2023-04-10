from variables import global_cam

def scroll_callback(window, xoffset, yoffset):
    print(global_cam.distance, yoffset)
    # if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS:
    
    if global_cam.toggle:
        print("orthogonal mode", global_cam.scale)
        if yoffset == 1.0:
        # zoom-out
            global_cam.scale += .01
        elif yoffset == -1.0 and global_cam.scale > 0.1:
        # zoom-in
            global_cam.scale -= .01
    else:
        # print("perspective mode")
        # print(global_cam.radius)
        if yoffset == 1.0 and global_cam.radius > 0.1:
            global_cam.add_radius(-0.01)
        elif yoffset == -1.0 and global_cam.radius < 10.:
            global_cam.add_radius(0.01)