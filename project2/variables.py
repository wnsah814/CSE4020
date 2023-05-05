import glm
class Camera:
    def __init__(self):
        self.distance = 10.0
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
        if tmp_dist < 0.01: 
            tmp_dist = 0.01
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
