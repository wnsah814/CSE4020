from OpenGL.GL import *
from variables import node_manager, load_obj

def drop_callback(window, paths):
    path = paths[0]
    node_manager.single_mash_mode = True
    vertices, normals, indices = load_obj(path)

    node_manager.set_single_node(None, vertices, normals, indices)