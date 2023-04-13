from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from variables import global_cam
from load_shaders import *
from key_callback import *
from mouse_button_callback import *
from cursor_position_callback import *
from scroll_callback import *
from vao import *

g_vertex_shader_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_color; 

out vec4 vout_color;

uniform mat4 MVP;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);
    gl_Position = MVP * p3D_in_hcoord;

    vout_color = vec4(vin_color, 1.);
}
'''

g_fragment_shader_src = '''
#version 330 core

in vec4 vout_color;

out vec4 FragColor;

void main()
{
    FragColor = vout_color;
}
'''

def main():
    # initialize glfw
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

    # create a window and OpenGL context
    window = glfwCreateWindow(800, 800, '2021092379', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    # register event callbacks
    glfwSetKeyCallback(window, key_callback);
    glfwSetCursorPosCallback(window, cursor_position_callback);
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    glfwSetScrollCallback(window, scroll_callback)

    # load shaders
    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

    # get uniform locations
    MVP_loc = glGetUniformLocation(shader_program, 'MVP')

    # prepare vaos
    vao_grid = prepare_vao_grid()
    vao_frame = prepare_vao_frame()
    vao_triangle = prepare_vao_triangle()
    # loop until the user closes the window
    while not glfwWindowShouldClose(window):
        # render
        # enable depth test (we'll see details later)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(shader_program)

        # projection matrix        
        P = global_cam.get_projection_matrix()
        # view matrix
        V = global_cam.get_view_matrix()

        I = glm.mat4()
        # current frame: P*V*I (now this is the world frame)

        # draw grid
        M = glm.mat4()
        GRID_START = -20
        GRID_END = 20
        GRID_STEP = 0.5

        glBindVertexArray(vao_grid)
        # X axis of grid
        for i in np.arange(GRID_START, GRID_END, GRID_STEP):
            # if i == 0: continue
            M = glm.translate(glm.vec3(0, 0, i))
            MVP = P*V*M
            glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_LINES, 0, 2)

        # Z axis of grid
        for i in np.arange(GRID_START, GRID_END, GRID_STEP):
            # if i == 0: continue
            M = glm.translate(glm.vec3(i, 0, 0))
            MVP = P*V*M
            glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_LINES, 2, 2)

        # # draw frame
        # # world frame
        # MVP = P*V*I
        # glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))

        # glBindVertexArray(vao_frame)
        # glDrawArrays(GL_LINES, 0, 6)
          
        # # animating
        # t = glfwGetTime()

        # # rotation
        # th = np.radians(t*90)
        # R = glm.rotate(th, glm.vec3(0,0,1))

        # # tranlation
        # # T = glm.translate(glm.vec3(offset_x, offset_y, offset_z));

        # # scaling
        # S = glm.scale(glm.vec3(np.sin(t), np.sin(t), np.sin(t)))

        # M = R @ T
        M = I
        # M = S
        # M = R @ T
        # M = T @ R

        # draw triangle
        # current frame: P*V*M
        MVP = P*V*M
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))

        # draw triangle w.r.t. the current frame
        glBindVertexArray(vao_triangle)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # swap front and back buffers
        glfwSwapBuffers(window)

        # poll events
        glfwPollEvents()

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    main()
