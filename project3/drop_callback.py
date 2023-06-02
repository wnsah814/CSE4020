from OpenGL.GL import *
from variables import load_bvh, joint_manager

def drop_callback(window, paths):
    path = paths[0]
    joints, frames = load_bvh(path)
    joint_manager.set_root(joints, frames)
    
    joint_manager.animate = False
    joint_manager.reset_joint_transform(joint_manager.root_joint)
    joint_manager.frow = 0
    joint_manager.fcol = 0