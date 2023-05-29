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










def make_triangles(vertices):
    new_vertices = []
    for i in range(0, len(vertices), 2):
        p1 = vertices[i]
        p2 = vertices[i + 1]
        new_vertices.append(p1.x - 1, p1.y, p1.z + 1)
        new_vertices.append(p1.x - 1, p1.y, p1.z - 1)
        new_vertices.append(p1.x + 1, p1.y, p1.z - 1)

        new_vertices.append(p1.x + 1, p1.y, p1.z - 1)
        new_vertices.append(p1.x + 1, p1.y, p1.z + 1)
        new_vertices.append(p1.x - 1, p1.y, p1.z - 1)






class JointManager:
    def __init__(self):
        self.root_joint = None
        self.frames = None
        self.frame_number = 0
        self.frame_time = 0
        self.vao = None
        self.count = 0          # len(vertices)
        self.animate = False    # is animate mode
        self.oldtime = 0        # for clock
        self.frow = 0           
        self.fcol = 0
        self.draw_index = 0

    def set_root(self, root_joint, frames):
        self.root_joint = root_joint
        self.frames = frames

        self.vao, self.count = create_vao(root_joint, frames)
        
    def update_joint_transform(self, joint):
        joint_transform = joint.joint_transform
        joint_transform = parse_joint_transform(joint, joint_manager.frames[joint_manager.frow][joint_manager.fcol:joint_manager.fcol + len(joint.channels)], glm.mat4())
        joint.set_joint_transform(joint_transform)
        # joint_transform = parse_joint_transform(joint, joint_manager.frames[joint_manager.frow][joint_manager.fcol:joint_manager.fcol + len(joint.channels)], joint_transform)
        
        joint_manager.fcol += len(joint.channels)

        # MVP = VP * joint.get_global_transform() * joint.get_shape_transform()
        # glUniformMatrix4fv(unif_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))

        # glDrawArrays(GL_LINES, joint.index, 2)

        for child in joint.children:
            self.update_joint_transform(child)

    def draw(self, joint, VP, unif_locs):
        # joint_transform = joint.joint_transform
        # joint_transform = parse_joint_transform(joint, joint_manager.frames[joint_manager.frow][joint_manager.fcol:joint_manager.fcol + len(joint.channels)], joint_transform)
        # joint_manager.fcol += len(joint.channels)
        # joint.set_joint_transform(joint_transform)
        # print(f"drawing {joint.name} ({joint.parent.name if joint.parent else joint.parent})\n{joint.link_transform_from_parent}")
        MVP = VP * joint.get_global_transform() * joint.get_shape_transform()
        glUniformMatrix4fv(unif_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        # if not joint.name == "End Site":
        glDrawArrays(GL_LINES, self.draw_index, 2)
        self.draw_index += 2

        for child in joint.children:
            self.draw(child, VP, unif_locs)

        if joint == self.root_joint:
            self.draw_index = 0

    def reset_joint_transform(self, joint):
        joint.set_joint_transform(glm.mat4())
        for child in joint.children:
            self.reset_joint_transform(child)

joint_manager = JointManager()

class Joint:
    def __init__(self, name, parent, link_transform_from_parent, shape_transform):
        self.name = name
        self.parent = parent
        self.children = []

        self.offset = None
        # 이게 아마 link transformation 일 것 같음.

        self.link_transform_from_parent = link_transform_from_parent
        self.joint_transform = glm.mat4()
        self.global_transform = glm.mat4()

        # shape
        self.shape_transform = shape_transform

        self.channels = []

        self.index = 0      # vao 시작 위치
    
    def print_hierarchy(self, lv = 0):
        print("\t"*lv, self.name)

        for child in self.children:
            child.print_hierarchy(lv+1)
    
    def printall(self):
        print("name", self.name, "index", self.index, "parent", self.parent, "offset", self.offset, "link", self.link_transform_from_parent, "joint", self.joint_transform, "global", self.global_transform, "shape", self.shape_transform, "channels", self.channels, sep="\n")
        # print('childrens', self.children)
        for child in self.children:
            print(child.index)

    def set_link_transform(self, link_transform):
        self.link_transform_from_parent = link_transform

    def set_joint_transform(self, joint_transform):
        self.joint_transform = joint_transform

    def update_tree_global_transform(self):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent * self.parent.joint_transform
        else:
            self.global_transform = self.link_transform_from_parent 

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
            joint_name = line.split()[1]
            current_joint = Joint(joint_name, None, glm.mat4(), glm.mat4())
            root_joint = current_joint
            joints[joint_name] = current_joint
        elif line.startswith('JOINT'):
            joint_name = line.split()[1]
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
            offset_values = line.split()[1:]
            offset = [float(value) for value in offset_values]
            current_joint.offset = glm.vec3(offset)
            current_joint.link_transform_from_parent = glm.vec3(offset)
        elif line.startswith('CHANNELS'):
            channel_values = line.split()[2:]
            channels = [channel.upper() for channel in channel_values]
            current_joint.channels = channels
        elif line.startswith('}'):
            current_joint = current_joint.parent

    print("parsed hierarchy")

    # Motion 정보 파싱
    joint_manager.frame_number = int(lines[motion_index + 1].split()[-1])
    joint_manager.frame_time = float(lines[motion_index + 2].split()[-1])

    motion_lines = lines[motion_index + 3:]
    # print(frame_number, frame_time, "motion lines")
    frame_index = 0
    frames = []

    while frame_index < len(motion_lines):
        frame_values = motion_lines[frame_index].split()
        frame_values = [float(value) for value in frame_values]
        frames.append(frame_values)
        frame_index += 1

    return root_joint, frames


# vao_start_index = 0
def create_vao(root_joint, frames):
    global vao_start_index
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # vertices = []
    vertices = [glm.vec3(0,0,0), glm.vec3(0,0,0)]
    # process_joint(root_joint, frames, vertices)

    # vao_start_index = 0
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

def process_joint(joint, vertices):
    # global vao_start_index

    # print(f"{joint.name}'s link transform {joint.offset}")    
    # joint.set_link_transform(glm.translate(joint.offset))
    joint.set_link_transform(glm.translate(joint.parent.offset if joint.parent is not None else glm.vec3(0, 0, 0)))
    # joint.index = vao_start_index
    # vao_start_index += 2

    if joint != joint_manager.root_joint:
        vertices.append(joint.offset)
        # vertices.append((glm.translate(joint.offset) * glm.vec4(0, 0, 0, 1)).xyz)
    
    for child in joint.children:
        vertices.append(glm.vec3(0, 0, 0))
        process_joint(child, vertices)
# def process_joint(joint, vertices, parent_transform = glm.mat4()):
#     global vao_start_index
    
#     joint.link_transform_from_parent = glm.translate(joint.offset)

#     joint.index = vao_start_index
#     vao_start_index += 2

#     joint_transform = glm.mat4(parent_transform) * glm.translate(joint.offset)
    
#     if joint != joint_manager.root_joint:
#         vertices.append((joint_transform * glm.vec4(0, 0, 0, 1)).xyz)
    
#     for child in joint.children:
#         vertices.append((joint_transform * glm.vec4(0, 0, 0, 1)).xyz)
#         process_joint(child, vertices, joint_transform)

def parse_joint_transform(joint, frame, joint_transform):
    for channel, value in zip(joint.channels, frame):
        # print("c", channel, "v", value);
        channel = channel.upper()
        value = float(value)
        if channel == 'XPOSITION':
            # print("value", value)
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