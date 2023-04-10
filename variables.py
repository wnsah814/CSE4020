import glm
import numpy as np
class Camera:
    def __init__(self, azimuth, elevation, height):
        self.azimuth = azimuth
        self.elevation = elevation
        self.height = height
        
        self.scale = 1.
        self.pan = glm.vec3(0.0, 0.0, 0.0)
        
        self.radius = 0.1
        self.eye = glm.vec3(self.radius*np.sin(self.azimuth)*np.sin(self.elevation),self.radius*np.cos(self.elevation),self.radius*np.cos(self.azimuth)*np.sin(self.elevation))
        self.center = glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.toggle = True
        self.distance = 1
        self.projection = glm.ortho(-self.distance,self.distance,-self.distance,self.distance,-self.distance,self.distance)
        # self.view = glm.lookAt(self.eye, self.center, self.up)
    def reset(self):
        self.azimuth = 0.
        self.elevation = glm.radians(45)
        self.height = .1
        
        self.scale = 1.
        self.pan = glm.vec3(0.0, 0.0, 0.0)
        
        self.radius = 0.1
        self.eye = glm.vec3(self.radius*np.sin(self.azimuth)*np.sin(self.elevation),self.radius*np.cos(self.elevation),self.radius*np.cos(self.azimuth)*np.sin(self.elevation))
        self.center = glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.toggle = True
        self.projection = glm.ortho(-self.distance,self.distance,-self.distance,self.distance,-self.distance,self.distance)
        
    def _set_projection(self):
        if self.toggle:
            self.projection = glm.ortho(-self.distance,self.distance,-self.distance,self.distance,-self.distance,self.distance)
        else:
            self.projection = glm.perspective(glm.radians(45.), 1., .01, 100.)
    
    def toggle_projection(self):
        self.toggle = not self.toggle
        self._set_projection()

    def add_distance(self, dist):
        self.distance += dist
        self._set_projection()
    # def get_right(self):
    #     return glm.cross(self.up, self.eye-self.center)
    
    # def get_up(self):
    #     return glm.cross(self.eye-self.center, self.get_right())
    
    # def move_left(self):
    #     self.eye += 0.1 * self.get_right()
    #     self.view = glm.lookAt(self.eye, self.center, self.up)
    
    def set_eye(self):
        # self.eye = glm.vec3(0.1*np.sin(self.angle),self.height,0.1*np.cos(self.angle))
        self.eye = glm.vec3(self.radius*np.sin(self.azimuth)*np.sin(self.elevation),self.radius*np.cos(self.elevation),self.radius*np.cos(self.azimuth)*np.sin(self.elevation))
    
    def add_azi(self, angle):
        self.azimuth += angle
        self.set_eye()

    def add_ele(self, angle):
        self.elevation += angle
        self.set_eye()

    def add_radius(self, r):
        self.radius += r;
        self.set_eye()
    # def add_height(self, height):
    #     self.height += height
    #     self.set_eye()


global_cam = Camera(0.0, 45.0, 0.1)


class Drag:
    def __init__(self, x, y):
        self.x = x
        self.y = y 
    def set_position(self, x, y):
        self.x = x
        self.y = y
    def get_position(self):
        return self.x, self.y

drag = Drag(0.0, 0.0)
