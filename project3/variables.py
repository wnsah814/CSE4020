from OpenGL.GL import *
import glm
import numpy as np
import ctypes
import os

class Camera:
    def __init__(self):
        self.distance = 15.0
        self.azimuth = glm.radians(135.)
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



class JointManager:
    def __init__(self):
        self.root_joint = None
        self.frames = None
        self.frame_number = 0
        self.frame_time = 0
        self.vao = None
        self.count = 0
        self.animate = False
        self.oldtime = 0

    def set_root(self, root_joint, frames):
        self.root_joint = root_joint
        self.frames = frames

        self.vao, self.count = create_vao(root_joint, frames)
        

joint_manager = JointManager()

class Joint:
    def __init__(self, name, parent, link_transform_from_parent, shape_transform):
        self.name = name
        self.parent = parent
        self.children = []
        # if parent is not None:
        #     parent.children.append(self)

        self.offset = None
        # 이게 아마 link transformation 일 것 같음.

        self.link_transform_from_parent = link_transform_from_parent
        self.joint_transform = glm.mat4()
        self.global_transform = glm.mat4()

        # shape
        self.shape_transform = shape_transform

        self.channels = []


    
    def printall(self):
        print("name", self.name, "parent", self.parent, "offset", self.offset, "link", self.link_transform_from_parent, "joint", self.joint_transform, "global", self.global_transform, "shape", self.shape_transform, "channels", self.channels, sep="\n")
        print('childrens', self.children)
        for child in self.children:
            print(child.name)

    def set_joint_transform(self, joint_transform):
        self.joint_transform = joint_transform

    def update_tree_global_transform(self):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent * self.joint_transform
        else:
            self.global_transform = self.link_transform_from_parent * self.joint_transform

        for child in self.children:
            child.update_tree_global_transform()

    def get_global_transform(self):
        return self.global_transform
    def get_shape_transform(self):
        return self.shape_transform

def load_bvh(filename):
    with open(filename, 'r') as file:
        data = file.read()

    lines = data.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    # Hierarchy 정보 파싱
    hierarchy_index = lines.index('HIERARCHY')
    motion_index = lines.index('MOTION')

    hierarchy_lines = lines[hierarchy_index + 1 : motion_index]

    # Hierarchy 파싱
    root_joint = None
    current_joint = None
    joints = {}

    for line in hierarchy_lines:
        if line.startswith('ROOT'):
            joint_name = line.split(' ')[1]
            current_joint = Joint(joint_name, None, glm.mat4(), glm.mat4())
            root_joint = current_joint
            joints[joint_name] = current_joint
        elif line.startswith('JOINT'):
            joint_name = line.split(' ')[1]
            joint = Joint(joint_name, current_joint, glm.mat4(), glm.mat4())
            # print(f"append {joint.name} to {current_joint.name}")
            current_joint.children.append(joint)
            joints[joint_name] = joint
            current_joint = joint
        elif line.startswith('End Site'):
            joint = Joint('End Site', current_joint, glm.mat4(), glm.mat4())
            # print(f"append {joint.name} to {current_joint.name}")
            current_joint.children.append(joint)
            current_joint = joint
        elif line.startswith('OFFSET'):
            offset_values = line.split(' ')[1:]
            offset = [float(value) for value in offset_values]
            current_joint.offset = glm.vec3(offset)
        elif line.startswith('CHANNELS'):
            channel_values = line.split(' ')[2:]
            channels = [channel.upper() for channel in channel_values]
            current_joint.channels = channels
        elif line.startswith('}'):
            current_joint = current_joint.parent

    print("parsed hierarchy")

    # Motion 정보 파싱
    joint_manager.frame_number = lines[motion_index + 1].split(' ')[-1]
    joint_manager.frame_time = lines[motion_index + 2].split(' ')[-1]

    motion_lines = lines[motion_index + 3:]
    # print(frame_number, frame_time, "motion lines")
    frame_index = 0
    frames = []

    while frame_index < len(motion_lines):
        frame_values = motion_lines[frame_index].split(' ')
        frame_values = [float(value) for value in frame_values]
        frames.append(frame_values)
        frame_index += 1

    return root_joint, frames

def create_vao(root_joint, frames):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vertices = []
    # process_joint(root_joint, frames, vertices)
    process_joint(root_joint, vertices)

    print("vertices", vertices, sep="\n")

    vertex_array = np.array(vertices, dtype=glm.float32)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertex_array, GL_STATIC_DRAW)

    # 버텍스 데이터 속성 설정
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # VAO 해제
    glBindVertexArray(0)

    return vao, len(vertices)

def process_joint(joint, vertices, parent_transform = glm.mat4()):
    joint_transform = glm.mat4(parent_transform) * glm.translate(joint.offset)
    vertices.append((joint_transform * glm.vec4(0, 0, 0, 1)).xyz)
    for child in joint.children:
        vertices.append((joint_transform * glm.vec4(0, 0, 0, 1)).xyz)
        process_joint(child, vertices, joint_transform)

def parse_joint_transform(joint, frame, joint_transform):
    for channel, value in zip(joint.channels, frame):
        print("c", channel, "v", value);
        channel = channel.upper()
        if channel == 'XPOSITION':
            print("xxxx")
            joint_transform = joint_transform * glm.translate((value, 0, 0))
            # joint_transform = np.dot(joint_transform, glm.translate((value, 0, 0)))
        elif channel == 'YPOSITION':
            joint_transform = joint_transform * glm.translate((0, value, 0))
            # joint_transform = np.dot(joint_transform, glm.translate((0, value, 0)))
        elif channel == 'ZPOSITION':
            joint_transform = joint_transform * glm.translate((0, 0, value))
            # joint_transform = np.dot(joint_transform, glm.translate((0, 0, value)))
        elif channel == 'XROTATION':
            joint_transform = joint_transform * glm.rotate(glm.radians(value), (1, 0, 0))
            # joint_transform = np.dot(joint_transform, glm.rotate(glm.radians(value), (1, 0, 0)))
        elif channel == 'YROTATION':
            joint_transform = joint_transform * glm.rotate(glm.radians(value), (0, 1, 0))
            # joint_transform = np.dot(joint_transform, glm.rotate(glm.radians(value), (0, 1, 0)))
        elif channel == 'ZROTATION':
            joint_transform = joint_transform * glm.rotate(glm.radians(value), (0, 0, 1))
            # joint_transform = np.dot(joint_transform, glm.rotate(glm.radians(value), (0, 0, 1)))
    return joint_transform
# def process_joint(joint, frames, vertices, parent_transform=glm.mat4()):
#     # 조인트의 변환 계산
#     # joint_transform = parent_transform.copy()
#     joint_transform = glm.mat4(parent_transform)
#     if joint.channels:
#         for frame in frames:
#             apply_joint_transform(joint, frame, joint_transform)

#     print(f"{joint.name}'s vertex... \n{joint_transform}")
#     # 조인트의 버텍스 생성
#     if joint.offset is not None:
#         vertex = np.dot(joint_transform, [0, 0, 0, 1])[:3]
#         vertices.append(vertex)

#     # 자식 조인트 처리
#     for child in joint.children:
#         process_joint(child, frames, vertices, joint_transform)

# def apply_joint_transform(joint, frame, joint_transform):
#     for channel, value in zip(joint.channels, frame):
#         print("c", channel, "v", value);
#         if channel == 'Xposition':
#             joint_transform = joint_transform * glm.translate((value, 0, 0))
#             # joint_transform = np.dot(joint_transform, glm.translate((value, 0, 0)))
#         elif channel == 'Yposition':
#             joint_transform = joint_transform * glm.translate((0, value, 0))
#             # joint_transform = np.dot(joint_transform, glm.translate((0, value, 0)))
#         elif channel == 'Zposition':
#             joint_transform = joint_transform * glm.translate((0, 0, value))
#             # joint_transform = np.dot(joint_transform, glm.translate((0, 0, value)))
#         elif channel == 'Xrotation':
#             joint_transform = joint_transform * glm.rotate(glm.radians(value), (1, 0, 0))
#             # joint_transform = np.dot(joint_transform, glm.rotate(glm.radians(value), (1, 0, 0)))
#         elif channel == 'Yrotation':
#             joint_transform = joint_transform * glm.rotate(glm.radians(value), (0, 1, 0))
#             # joint_transform = np.dot(joint_transform, glm.rotate(glm.radians(value), (0, 1, 0)))
#         elif channel == 'Zrotation':
#             joint_transform = joint_transform * glm.rotate(glm.radians(value), (0, 0, 1))
#             # joint_transform = np.dot(joint_transform, glm.rotate(glm.radians(value), (0, 0, 1)))






# def _parse_indices(vertices, normals, indices):
#     result = []
#     for idx in indices:
#         result.append(vertices[idx[0]])
#         result.append(normals[idx[1]])
#     return glm.array(np.array(result))

# def _create_vao(vertices, normals, indices):
#     result = _parse_indices(vertices, normals, indices)
#     vao = glGenVertexArrays(1)
#     glBindVertexArray(vao)

#     vbo = glGenBuffers(1)
#     glBindBuffer(GL_ARRAY_BUFFER, vbo)
#     glBufferData(GL_ARRAY_BUFFER, result.nbytes, result.ptr, GL_STATIC_DRAW)
#     glEnableVertexAttribArray(0)
#     glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
#     glEnableVertexAttribArray(1)
#     glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(glm.sizeof(glm.float32) * 3))
        
#     glBindVertexArray(0)
#     return vao, int(len(result) / 2)

# class NodeManager:
#     def __init__(self):
#         self.hierarch_nodes = {}
#         self.sigle_node = None
#         self.single_mash_mode = True
#         self.wire_frame_mode = False

#     def append_node(self, name, parent, shape, color, vertices, normals, indices):
#         self.hierarch_nodes[name] = Node(parent, shape, color, vertices, normals, indices)

#     def set_single_node(self, parent, vertices, normals, indices):
#         self.sigle_node = Node(parent, glm.mat4(), glm.vec3(1,1,1), vertices, normals, indices)

#     def toggle_render_mode(self):
#         self.single_mash_mode = not self.single_mash_mode
#     def toggle_frame_mode(self):
#         self.wire_frame_mode = not self.wire_frame_mode


# node_manager = NodeManager();
# class Node:
#     def __init__(self, parent, shape_transform, color, vertices, normals, indices):
#         # vao
#         self.vao, self.length = _create_vao(vertices, normals, indices)
#         # hierarchy
#         self.parent = parent
#         self.children = []
#         if parent is not None:
#             parent.children.append(self)

#         # transform
#         self.transform = glm.mat4()
#         self.global_transform = glm.mat4()

#         # shape
#         self.shape_transform = shape_transform
#         self.color = color

#     def set_transform(self, transform):
#         self.transform = transform

#     def update_tree_global_transform(self):
#         if self.parent is not None:
#             self.global_transform = self.parent.get_global_transform() * self.transform
#         else:
#             self.global_transform = self.transform

#         for child in self.children:
#             child.update_tree_global_transform()

#     def draw_node(self, VP, unif_locs):
#         M = self.get_global_transform() * self.get_shape_transform()
#         MVP = VP * M
#         color = self.get_color()

#         glBindVertexArray(self.vao)
        
#         glUniformMatrix4fv(unif_locs["M"], 1, GL_FALSE, glm.value_ptr(M))
#         glUniformMatrix4fv(unif_locs["MVP"], 1, GL_FALSE, glm.value_ptr(MVP))
#         glUniform3f(unif_locs["material_color"], color.r, color.g, color.b)
#         glDrawArrays(GL_TRIANGLES, 0, self.length)
    
#     def get_vao(self):
#         return self.vao
#     def get_length(self):
#         return self.length
#     def get_global_transform(self):
#         return self.global_transform
#     def get_shape_transform(self):
#         return self.shape_transform
#     def get_color(self):
#         return self.color

