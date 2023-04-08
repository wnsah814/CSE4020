import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import *
import glm

class Camera:
    def __init__(self, pos=[0,0,0], target=[0,0,-1], up=[0,1,0], fov=45):
        self.pos = pos
        self.target = target
        self.up = up
        self.fov = fov
        self.speed = 5.0
        self.sensitivity = 0.1
        
    def update(self, window, deltaTime):
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        x, y = glfw.get_cursor_pos(window)
        glfw.set_cursor_pos(window, 800/2, 600/2)
        dx, dy = 800/2 - x, 600/2 - y
        
        dx *= self.sensitivity
        dy *= self.sensitivity
        
        cam_dir = glm.normalize([self.target[0]-self.pos[0], self.target[1]-self.pos[1], self.target[2]-self.pos[2]])
        cam_right = glm.normalize(glm.cross(cam_dir, self.up))
        cam_up = glm.cross(cam_right, cam_dir)
        
        self.target[0] += dx * cam_right[0] + dy * cam_up[0]
        self.target[1] += dy * cam_up[1]
        self.target[2] += dx * cam_right[2] + dy * cam_up[2]
        
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.pos[0] += cam_dir[0] * self.speed * deltaTime
            self.pos[1] += cam_dir[1] * self.speed * deltaTime
            self.pos[2] += cam_dir[2] * self.speed * deltaTime
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.pos[0] -= cam_dir[0] * self.speed * deltaTime
            self.pos[1] -= cam_dir[1] * self.speed * deltaTime
            self.pos[2] -= cam_dir[2] * self.speed * deltaTime
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.pos[0] -= cam_right[0] * self.speed * deltaTime
            self.pos[1] -= cam_right[1] * self.speed * deltaTime
            self.pos[2] -= cam_right[2] * self.speed * deltaTime
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.pos[0] += cam_right[0] * self.speed * deltaTime
            self.pos[1] += cam_right[1] * self.speed * deltaTime
            self.pos[2] += cam_right[2] * self.speed * deltaTime
            
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # gluPerspective(self.fov, 800/600, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # gluLookAt(self.pos[0], self.pos[1], self.pos[2], self.target[0], self.target[1], self.target[2], self.up[0], self.up[1], self.up[2])


def main():
    # initialize GLFW
    if not glfw.init():
        return
    
    # create a window
    window = glfw.create_window(800, 600, "Modern OpenGL", None, None)
    if not window:
        glfw.terminate()
        return
    
    # make the window's context current
    glfw.make_context_current(window)
    
    # create a shader program
    vertex_shader = """
        #version 330
        
        layout (location = 0) in vec3 position;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        void main() {
            gl_Position = projection * view * model * vec4(position, 1.0);
        }
    """
    fragment_shader = """
        #version 330
        
        out vec4 color;
        
        void main() {
            color = vec4(1.0, 1.0, 1.0, 1.0);
        }
    """
    shader_program = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER), compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    
    # create a vertex buffer object (VBO) and a vertex array object (VAO)
    vertices = [-0.5, -0.5, 0.0,  # bottom left
                0.5, -0.5, 0.0,  # bottom right
                0.0,  0.5, 0.0]  # top
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    # set up the camera
    camera = Camera()
    
    # enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # render loop
    while not glfw.window_should_close(window):
        # update the camera
        deltaTime = glfw.get_time()
        camera.update(window, deltaTime)
        
        # clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # draw the triangle
        glUseProgram(shader_program)
        model = glm.mat4(1.0)
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(camera.get_view_matrix()))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(glm.perspective(glm.radians(camera.fov), 800/600, 0.1, 100.0)))
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        
        # swap the front and back buffers
        glfw.swap_buffers(window)
        
        # poll for and process events
        glfw.poll_events()
    
    # clean up
    glfw.terminate()

if __name__ == "__main__":
    main()
