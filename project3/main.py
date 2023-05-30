from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np
import os
from variables import global_cam, joint_manager, parse_joint_transform
from load_shaders import *
from key_callback import *
from mouse_button_callback import *
from cursor_position_callback import *
from scroll_callback import *
from drop_callback import *
from vao import *

g_vertex_shader_src_pos = '''
#version 330 core

layout (location = 0) in vec3 vin_pos;

out vec4 vout_color;

uniform mat4 MVP;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);
    gl_Position = MVP * p3D_in_hcoord;
    vout_color = vec4(1, 1, 0, 1);
}

'''
g_vertex_shader_src_color = '''
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
g_vertex_shader_src_normal = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_normal; 

out vec3 vout_surface_pos;
out vec3 vout_normal;

uniform mat4 MVP;
uniform mat4 M;

void main()
{
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);
    gl_Position = MVP * p3D_in_hcoord;

    vout_surface_pos = vec3(M * vec4(vin_pos, 1));
    vout_normal = normalize( mat3(inverse(transpose(M)) ) * vin_normal);
}
'''

g_fragment_shader_src_color = '''
#version 330 core

in vec4 vout_color;

out vec4 FragColor;

void main()
{
    FragColor = vout_color;
}
'''

g_fragment_shader_src_normal = '''
#version 330 core

in vec3 vout_surface_pos;
in vec3 vout_normal;  // interpolated normal

out vec4 FragColor;

uniform vec3 view_pos;

void main()
{
    // light and material properties
    vec3 light_pos = vec3(-3,2,4);
    vec3 light_color = vec3(1,1,1);
    vec3 material_color = vec3(1,0,0);
    float material_shininess = 32.0;

    // light components
    vec3 light_ambient = 0.1*light_color;
    vec3 light_diffuse = light_color;
    vec3 light_specular = light_color;

    // material components
    vec3 material_ambient = material_color;
    vec3 material_diffuse = material_color;
    vec3 material_specular = light_color;  // for non-metal material

    // ambient
    vec3 ambient = light_ambient * material_ambient;

    // for diffiuse and specular
    vec3 normal = normalize(vout_normal);
    vec3 surface_pos = vout_surface_pos;
    vec3 light_dir = normalize(light_pos - surface_pos);

    // diffuse
    float diff = max(dot(normal, light_dir), 0);
    vec3 diffuse = diff * light_diffuse * material_diffuse;

    // specular
    vec3 view_dir = normalize(view_pos - surface_pos);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float spec = pow( max(dot(view_dir, reflect_dir), 0.0), material_shininess);
    vec3 specular = spec * light_specular * material_specular;

    vec3 color = ambient + diffuse + specular;
    FragColor = vec4(color, 1.);
}
'''

def draw_grid(vao, VP, unif_locs_color):
    M = glm.mat4()

    GRID_START = -20
    GRID_END = 21
    GRID_STEP = 1

    glBindVertexArray(vao)
    # X axis of grid
    for i in np.arange(GRID_START, GRID_END, GRID_STEP):
        M = glm.translate(glm.vec3(0, 0, i))
        MVP = VP * M
        glUniformMatrix4fv(unif_locs_color['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawArrays(GL_LINES, 0, 2)

    # Z axis of grid
    for i in np.arange(GRID_START, GRID_END, GRID_STEP):
        M = glm.translate(glm.vec3(i, 0, 0))
        MVP = VP * M
        glUniformMatrix4fv(unif_locs_color['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawArrays(GL_LINES, 2, 2)
          

def main():
    # initialize glfw
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

    # create a window and OpenGL context
    window = glfwCreateWindow(800, 800, '2021092379_project2', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    # register event callbacks
    glfwSetKeyCallback(window, key_callback);
    glfwSetCursorPosCallback(window, cursor_position_callback);
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    glfwSetScrollCallback(window, scroll_callback)
    glfwSetDropCallback(window, drop_callback)
    # load shaders
    shader_pos = load_shaders(g_vertex_shader_src_pos, g_fragment_shader_src_color)
    unif_names = ['MVP']
    unif_locs_pos = {}
    for name in unif_names:
        unif_locs_pos[name] = glGetUniformLocation(shader_pos, name)

    shader_color = load_shaders(g_vertex_shader_src_color, g_fragment_shader_src_color)
    unif_names = ['MVP']
    unif_locs_color = {}
    for name in unif_names:
        unif_locs_color[name] = glGetUniformLocation(shader_color, name)

    shader_normal = load_shaders(g_vertex_shader_src_normal, g_fragment_shader_src_normal)
    unif_names = ['MVP', 'M', 'view_pos', 'material_color']
    unif_locs_normal = {}
    for name in unif_names:
        unif_locs_normal[name] = glGetUniformLocation(shader_normal, name)

    # prepare vaos
    vao_grid = prepare_vao_grid()
    vao_cube = prepare_vao_cube()
    # loop until the user closes the window
    while not glfwWindowShouldClose(window):
        # render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # projection matrix
        P = global_cam.get_projection_matrix()
        # view matrix
        V = global_cam.get_view_matrix()
        view_pos = global_cam.get_eye() + global_cam.pan

        glUseProgram(shader_color)
        draw_grid(vao_grid, P * V, unif_locs_color)

        if joint_manager.vao is not None:
            glUseProgram(shader_pos)
            glBindVertexArray(joint_manager.vao)

            if joint_manager.animate:
                newtime = glfwGetTime()
                if newtime - joint_manager.oldtime >= joint_manager.frame_time:
                    joint_manager.oldtime = newtime
                    joint_manager.frow += 1
                    # print(joint_manager.frow)
                    if (joint_manager.frow >= joint_manager.frame_number):
                        joint_manager.frow = 0
                        joint_manager.reset_joint_transform(joint_manager.root_joint)
                        joint_manager.root_joint.update_tree_global_transform()
                    joint_manager.fcol = 0
                    joint_manager.update_joint_transform(joint_manager.root_joint)
                    joint_manager.root_joint.update_tree_global_transform()
                
                if joint_manager.boxmode:
                    glUseProgram(shader_normal)
                    glBindVertexArray(vao_cube)
                    glUniform3f(unif_locs_normal['view_pos'], view_pos.x, view_pos.y, view_pos.z)
                    joint_manager.draw_box(joint_manager.root_joint, P * V, unif_locs_normal)
                else:
                    glUseProgram(shader_pos)
                    glBindVertexArray(joint_manager.vao)
                    joint_manager.draw(joint_manager.root_joint, P * V, unif_locs_pos)
                
                # MVP = P * V * joint.get_global_transform() * joint.get_shape_transform()
                # glUniformMatrix4fv(unif_locs_pos['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
                
                # glDrawArrays(GL_LINES, joint.index, 2)
                # for idx in range(0, joint_manager.count, 2):
                #     glDrawArrays(GL_LINES, idx, 2)
            else:
                # M = glm.mat4()
                joint_manager.reset_joint_transform(joint_manager.root_joint)

                joint_manager.root_joint.update_tree_global_transform()
                
                if joint_manager.boxmode:
                    glUseProgram(shader_normal)
                    glBindVertexArray(vao_cube)
                    glUniform3f(unif_locs_normal['view_pos'], view_pos.x, view_pos.y, view_pos.z)
                    joint_manager.draw_box(joint_manager.root_joint, P * V, unif_locs_normal)
                else:
                    glUseProgram(shader_pos)
                    glBindVertexArray(joint_manager.vao)
                    joint_manager.draw(joint_manager.root_joint, P * V, unif_locs_pos)
                # for idx in range(0, joint_manager.count, 2):
                #     MVP = P * V * 
                #     glUniformMatrix4fv(unif_locs_pos['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
                #     glDrawArrays(GL_LINES, idx, 2)
                # glDrawArrays(GL_LINES, 0, joint_manager.count)
            
        # swap front and back buffers
        glfwSwapBuffers(window)

        # poll events
        glfwPollEvents()

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    main()
