from OpenGL.GL import *
import glm
import numpy as np
import os

class Camera:
    def __init__(self):
        self.distance = 250.0
        self.azimuth = glm.radians(135)
        self.elevation = glm.radians(45)

        self.pan = glm.vec3(0, 0, 0)
        self.center = glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 1, 0)

        self.is_projection = True
    
    def get_eye(self):
        return glm.vec3(self.distance * glm.sin(self.azimuth) * glm.sin(self.elevation), self.distance * glm.cos(self.elevation), self.distance * glm.cos(self.azimuth) * glm.sin(self.elevation))
    
    def get_view_matrix(self):
        return glm.lookAt(self.get_eye() + self.pan, self.center + self.pan, self.up)
    
    def get_projection_matrix(self): 
        return glm.perspective(glm.radians(45), 1, .1, 1000) if self.is_projection else glm.ortho(-self.distance / 2.45, self.distance / 2.45, -self.distance / 2.45, self.distance / 2.45, -1000, 1000)

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
        elif tmp_dist > 500: 
            tmp_dist = 500
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
        self.count = 0          # len(vertices)
        self.animate = False    # is animate mode
        self.boxmode = False    # is box rendering mode
        self.oldtime = 0        # for clock
        self.frow = 0           
        self.fcol = 0
        self.draw_index = 0

    def set_root(self, root_joint, frames):
        self.root_joint = root_joint
        self.frames = frames
        self.vao, self.count = create_vao(root_joint)
    
    def draw_box(self, joint, VP, unif_locs):
        len = glm.length(joint.offset)
        vec1 = glm.vec3(0, 1, 0)
        vec2 = glm.normalize(joint.offset)

        dot = glm.dot(vec1, vec2)
        cross = glm.cross(vec1, vec2)
        if glm.length(cross) == 0:
            cross = glm.vec3(0, 1, 0)

        axis = glm.normalize(cross)
        angle = glm.acos(dot)

        rotate = glm.rotate(angle, axis)
        
        M = joint.get_global_transform() * joint.get_shape_transform() * rotate *  glm.scale((1, len / 2, 1)) * glm.translate((0, 1, 0))
        MVP = VP * M
        glUniformMatrix4fv(unif_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        glUniformMatrix4fv(unif_locs['M'], 1, GL_FALSE, glm.value_ptr(M))
        
        glDrawArrays(GL_TRIANGLES, 0, 36)

        for child in joint.children:
            self.draw_box(child, VP, unif_locs)

    def draw_line(self, joint, VP, unif_locs):
        MVP = VP * joint.get_global_transform() * joint.get_shape_transform()
        glUniformMatrix4fv(unif_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawArrays(GL_LINES, self.draw_index, 2)
        self.draw_index += 2

        for child in joint.children:
            self.draw_line(child, VP, unif_locs)

        if joint == self.root_joint:
            self.draw_index = 0

    def update_joint_transform(self, joint):
        joint_transform = joint.joint_transform
        joint_transform = parse_joint_transform(joint, joint_manager.frames[joint_manager.frow][joint_manager.fcol:joint_manager.fcol + len(joint.channels)], glm.mat4())
        joint.set_joint_transform(joint_transform)
        
        joint_manager.fcol += len(joint.channels)

        for child in joint.children:
            self.update_joint_transform(child)

    def reset_joint_transform(self, joint):
        joint.set_joint_transform(glm.mat4())
        for child in joint.children:
            self.reset_joint_transform(child)

joint_manager = JointManager()

class Joint:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children = []

        self.offset = None

        self.link_transform_from_parent = glm.mat4()
        self.joint_transform = glm.mat4()
        self.global_transform = glm.mat4()
        self.shape_transform = glm.mat4()

        self.channels = []

        self.index = 0      # vao 시작 위치

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

    def print_hierarchy(self, lv = 0):
        print("  " * lv, self.name, sep="")
        for child in self.children:
            child.print_hierarchy(lv + 1)

def load_bvh(filename):
    with open(filename, 'r') as file:
        data = file.read()

    lines = data.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    hierarchy_index = lines.index('HIERARCHY')
    motion_index = lines.index('MOTION')

    hierarchy_lines = lines[hierarchy_index + 1 : motion_index]

    root_joint = None
    current_joint = None
    joints = {}

    for line in hierarchy_lines:
        if line.startswith('ROOT'):
            joint_name = line.split()[1]
            current_joint = Joint(joint_name, None)
            root_joint = current_joint
            joints[joint_name] = current_joint
        elif line.startswith('JOINT'):
            joint_name = line.split()[1]
            joint = Joint(joint_name, current_joint)
            current_joint.children.append(joint)
            joints[joint_name] = joint
            current_joint = joint
        elif line.startswith('End Site'):
            joint = Joint('End Site', current_joint)
            current_joint.children.append(joint)
            current_joint = joint
        elif line.startswith('OFFSET'):
            offset_values = line.split()[1:]
            offset = [float(value) for value in offset_values]
            current_joint.offset = glm.vec3(offset)
        elif line.startswith('CHANNELS'):
            channel_values = line.split()[2:]
            channels = [channel.upper() for channel in channel_values]
            current_joint.channels = channels
        elif line.startswith('}'):
            current_joint = current_joint.parent

    frame_number = int(lines[motion_index + 1].split()[-1])
    frame_time = float(lines[motion_index + 2].split()[-1])
    
    joint_manager.frame_time = frame_time
    joint_manager.frame_number = frame_number

    motion_lines = lines[motion_index + 3:]
    frame_index = 0
    frames = []

    while frame_index < len(motion_lines):
        frame_values = motion_lines[frame_index].split()
        frame_values = [float(value) for value in frame_values]
        frames.append(frame_values)
        frame_index += 1

    print("File Name:", os.path.splitext(os.path.basename(filename))[0])
    print("Number of Frames:", frame_number)
    print("FPS:", 1 / frame_time)
    print("Number of Joints:", len(joints))
    print("Joints List:")
    root_joint.print_hierarchy()

    return root_joint, frames

def create_vao(root_joint):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vertices = []

    process_joint(root_joint, vertices)

    vertex_array = np.array(vertices, dtype=glm.float32)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertex_array, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    glBindVertexArray(0)

    return vao, len(vertices)

def process_joint(joint, vertices):
    joint.set_link_transform(glm.translate(joint.parent.offset if joint.parent is not None else glm.vec3(0, 0, 0)))

    vertices.append(glm.vec3(0, 0, 0))
    vertices.append(joint.offset)
    
    for child in joint.children:
        process_joint(child, vertices)

def parse_joint_transform(joint, frame, joint_transform):
    for channel, value in zip(joint.channels, frame):
        channel = channel.upper()
        value = float(value)
        if channel == 'XPOSITION':
            joint_transform = joint_transform * glm.translate((value, 0, 0))
        elif channel == 'YPOSITION':
            joint_transform = joint_transform * glm.translate((0, value, 0))
        elif channel == 'ZPOSITION':
            joint_transform = joint_transform * glm.translate((0, 0, value))
        elif channel == 'XROTATION':
            joint_transform = joint_transform * glm.rotate(glm.radians(value), (1, 0, 0))
        elif channel == 'YROTATION':
            joint_transform = joint_transform * glm.rotate(glm.radians(value), (0, 1, 0))
        elif channel == 'ZROTATION':
            joint_transform = joint_transform * glm.rotate(glm.radians(value), (0, 0, 1))
    return joint_transform