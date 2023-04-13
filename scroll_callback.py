from variables import global_cam

def scroll_callback(window, xoffset, yoffset):
    if not global_cam.is_projection:
        return
    if yoffset == 1.0 and global_cam.distance > 0.1:
        global_cam.add_distance(-0.05)
    elif yoffset == -1.0 and global_cam.distance < 30.:
        global_cam.add_distance(0.05)

    # print(global_cam.distance)