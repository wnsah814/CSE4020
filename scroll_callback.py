from variables import global_cam

def scroll_callback(window, xoffset, yoffset):
    MAX = 20.0
    MIN = 1.0
    print(global_cam.distance, yoffset)
    if yoffset == -1.0 and global_cam.distance < MAX:
        print("mouse scrolled down")
        global_cam.add_distance(0.1)
        # global_cam.add_radius(0.1)
    elif yoffset == 1.0 and global_cam.distance > MIN:
        print("mouse scrolled up")
        global_cam.add_distance(-0.1)
        # global_cam.add_radius(-0.1)