from variables import global_cam

def scroll_callback(window, xoffset, yoffset):
    if not global_cam.is_projection:
        return
    global_cam.add_distance(0.01 * yoffset)