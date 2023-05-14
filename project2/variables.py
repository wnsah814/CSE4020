from OpenGL.GL import *
import glm
import numpy as np
import ctypes
import os

class Camera:
    def __init__(self):
        self.distance = 20.0
        self.azimuth = glm.radians(45.)
        self.elevation = glm.radians(45.)

        self.pan = glm.vec3(0.0, 0.0, 0.0)
        self.center = glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 1, 0)

        self.is_projection = True
    
    def get_eye(self):
        return glm.vec3(self.distance * glm.sin(self.azimuth) * glm.sin(self.elevation), self.distance * glm.cos(self.elevation), self.distance * glm.cos(self.azimuth) * glm.sin(self.elevation))
    
    def get_view_matrix(self):
        return glm.lookAt(self.get_eye() + self.pan, self.center + self.pan, self.up)
    
    def get_projection_matrix(self): 
        return glm.perspective(glm.radians(45.), 1., .1, 50.) if self.is_projection else glm.ortho(-self.distance / 2.45, self.distance / 2.45, -self.distance / 2.45, self.distance / 2.45, -50, 50)

    def toggle_projection(self):
        self.is_projection = not self.is_projection
    
    def add_azi(self, angle):
        self.azimuth += angle

    def add_ele(self, angle):
        self.elevation += angle

    def add_distance(self, d):
        tmp_dist = self.distance + d
        if tmp_dist < 0.2: 
            tmp_dist = 0.2
        elif tmp_dist > 40: 
            tmp_dist = 40
        self.distance = tmp_dist
        
global_cam = Camera()

class Drag:
    def __init__(self):
        self.x = 0.
        self.y = 0.
    def set_position(self, x, y):
        self.x = x
        self.y = y
    def get_position(self):
        return self.x, self.y

drag = Drag()

def load_obj(file_path):
    vertices = []
    normals = []
    indices = []
    face3 = 0
    face4 = 0
    face5 = 0
    with open(file_path) as f:
        for line in f:
            tokens = line.split()
            if not tokens:
                continue
            if tokens[0] == 'v':
                vertex = [float(x) for x in tokens[1:]]
                vertices.append(glm.vec3(vertex))
            elif tokens[0] == 'vn':
                normal = [float(x) for x in tokens[1:]]
                normals.append(glm.vec3(normal))
            elif tokens[0] == 'f':
                num_tokens = len(tokens[1:])
                if num_tokens == 3:
                    face3 += 1
                elif num_tokens == 4:
                    face4 += 1
                else:
                    face5 += 1
                for i in range(1, len(tokens[1:]) - 1):
                    for face_token in tokens[1], tokens[i + 1], tokens[i + 2]:
                        index_data = face_token.split('/')
                        vertex_index = int(index_data[0]) - 1
                        normal_index = 0
                        if len(index_data) > 1:
                            normal_index = int(index_data[2]) - 1
                        indices.append(glm.ivec2(vertex_index, normal_index))
    if node_manager.single_mash_mode:
        print("obj file name: ", os.path.splitext(os.path.basename(file_path))[0])
        print("Total number of faces: ", face3 + face4 + face5)
        print("Number of faces with 3 vertices: ", face3)
        print("Number of faces with 4 vertices: ", face4)
        print("Number of faces with more than 4 vertices: ", face5)

    return glm.array(vertices), glm.array(normals), glm.array(indices)

def _parse_indices(vertices, normals, indices):
    result = []
    for idx in indices:
        result.append(vertices[idx[0]])
        result.append(normals[idx[1]])
    return glm.array(np.array(result))

def _create_vao(vertices, normals, indices):
    result = _parse_indices(vertices, normals, indices)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, result.nbytes, result.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(glm.sizeof(glm.float32) * 3))
        
    glBindVertexArray(0)
    return vao, int(len(result) / 2)

class NodeManager:
    def __init__(self):
        self.hierarch_nodes = {}
        self.sigle_node = None
        self.single_mash_mode = True
        self.wire_frame_mode = False

    def append_node(self, name, parent, shape, color, vertices, normals, indices):
        self.hierarch_nodes[name] = Node(parent, shape, color, vertices, normals, indices)

    def set_single_node(self, parent, vertices, normals, indices):
        self.sigle_node = Node(parent, glm.scale(glm.vec3(0.2, .2, .2)), glm.vec3(1,1,1), vertices, normals, indices)

    def toggle_render_mode(self):
        self.single_mash_mode = not self.single_mash_mode
    def toggle_frame_mode(self):
        self.wire_frame_mode = not self.wire_frame_mode


node_manager = NodeManager();
class Node:
    def __init__(self, parent, shape_transform, color, vertices, normals, indices):
        # vao
        self.vao, self.length = _create_vao(vertices, normals, indices)
        # hierarchy
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)

        # transform
        self.transform = glm.mat4()
        self.global_transform = glm.mat4()

        # shape
        self.shape_transform = shape_transform
        self.color = color

    def set_transform(self, transform):
        self.transform = transform

    def update_tree_global_transform(self):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.transform
        else:
            self.global_transform = self.transform

        for child in self.children:
            child.update_tree_global_transform()

    def draw_node(self, VP, unif_locs):
        M = self.get_global_transform() * self.get_shape_transform()
        MVP = VP * M
        color = self.get_color()

        glBindVertexArray(self.vao)
        
        glUniformMatrix4fv(unif_locs["M"], 1, GL_FALSE, glm.value_ptr(M))
        glUniformMatrix4fv(unif_locs["MVP"], 1, GL_FALSE, glm.value_ptr(MVP))
        glUniform3f(unif_locs["material_color"], color.r, color.g, color.b)
        glDrawArrays(GL_TRIANGLES, 0, self.length)
    
    def get_vao(self):
        return self.vao
    def get_length(self):
        return self.length
    def get_global_transform(self):
        return self.global_transform
    def get_shape_transform(self):
        return self.shape_transform
    def get_color(self):
        return self.color

