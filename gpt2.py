import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import glm
# vertex shader
VERTEX_SHADER = """
#version 330
layout (location = 0) in vec3 a_position;

uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

void main() {
    gl_Position = u_projection_matrix * u_view_matrix * vec4(a_position, 1.0);
}
"""

# fragment shader
FRAGMENT_SHADER = """
#version 330
out vec4 out_color;

void main() {
    out_color = vec4(1.0, 1.0, 1.0, 1.0);
}
"""

# grid properties
GRID_SIZE = 20
GRID_STEP = 1

# create XZ plane grid vertices
vertices = []
for i in range(-GRID_SIZE, GRID_SIZE + 1, GRID_STEP):
    vertices.append([i, 0.0, -GRID_SIZE])
    vertices.append([i, 0.0, GRID_SIZE])
    vertices.append([-GRID_SIZE, 0.0, i])
    vertices.append([GRID_SIZE, 0.0, i])
vertices = np.array(vertices, dtype=np.float32)

# create a window
if not glfw.init():
    raise Exception("GLFW initialization failed")
window = glfw.create_window(800, 600, "XZ Plane Grid", None, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window creation failed")
glfw.make_context_current(window)

# compile shaders and create shader program
vertex_shader = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
fragment_shader = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
shader_program = compileProgram(vertex_shader, fragment_shader)

# get uniform locations
view_matrix_loc = glGetUniformLocation(shader_program, "u_view_matrix")
projection_matrix_loc = glGetUniformLocation(shader_program, "u_projection_matrix")

# enable depth testing and set clear color
glEnable(GL_DEPTH_TEST)
glClearColor(0.0, 0.0, 0.0, 1.0)

# render loop
while not glfw.window_should_close(window):
    # clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # set the shader program
    glUseProgram(shader_program)
    
    # set the view matrix (no camera used in this example, so use identity matrix)
    view_matrix = np.identity(4, dtype=np.float32)
    glUniformMatrix4fv(view_matrix_loc, 1, GL_FALSE, view_matrix)
    
    # set the projection matrix
    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height
    projection_matrix = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)
    glUniformMatrix4fv(projection_matrix_loc, 1, GL_FALSE, projection_matrix.to_list())
    
    # draw the XZ plane grid
    glBindVertexArray(0)
    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glDrawArrays(GL_LINES, 0, len(vertices))
    glBindVertexArray(0)
    
    # poll for and process events
    glfw.poll_events()
    glfw.swap_buffers(window)

# clean up
glfw.terminate()
