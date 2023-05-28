from OpenGL.GL import *
from variables import load_bvh, joint_manager

def drop_callback(window, paths):
    path = paths[0]
    joints, frames = load_bvh(path)
    joint_manager.set_root(joints, frames)
    # print("joints", joints, "frames", frames, sep="\n")
    # joints.printall()