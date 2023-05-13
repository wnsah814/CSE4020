from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np
import os
from variables import global_cam, node_manager, load_obj
from load_shaders import *
from key_callback import *
from mouse_button_callback import *
from cursor_position_callback import *
from scroll_callback import *
from drop_callback import *
from vao import *

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
    vout_normal = normalize( mat3(transpose(inverse(M))) * vin_normal);
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

g_fragment_shader_src_normal_x = '''
#version 330 core

#define NLIGHT 3

in vec3 vout_surface_pos;
in vec3 vout_normal;

out vec4 FragColor;

uniform vec3 view_pos;
uniform vec3 material_color;

void main()
{
    // light and material properties
    vec3 light_pos = vec3(100, 100, -100);
    vec3 light_color = vec3(1,1,1);
    // vec3 material_color = vec3(156, 167, 119) * 0.004;
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
g_fragment_shader_src_normal = '''
#version 330 core

#define NLIGHT 3

in vec3 vout_surface_pos;
in vec3 vout_normal;

out vec4 FragColor;

uniform vec3 view_pos;
uniform vec3 material_color;

struct Light {
    vec3 pos;
    vec3 color;
};

vec3 calcLight(Light light) {
    vec3 light_pos = light.pos;
    vec3 light_color = light.color;
    // light and material properties
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
    return color;
}

void main()
{
    //vec3 light_pos[3] = {vec3(10, 10, 10), vec3(-10, -10, -10), vec3(10, 10, -10)};
    //vec3 light_pos[3] = vec3[3](vec3(10, 10, 10), vec3(-10, -10, -10), vec3(10, 10, -10));
    
    /*
    Light lights[3] = {
        Light(vec3(10, 10, 10), vec3(1, 0, 0)),
        Light(vec3(10, -10, 10), vec3(0, 1, 0)),
        Light(vec3(10, 10, 110), vec3(0, 0, 1)),
    };
    */

    /*    
    Light lights[3] = Light[3](
        Light(vec3(20, 20, 20), vec3(1, 0, 0)),
        Light(vec3(20, -20, 20), vec3(0, 1, 0)),
        Light(vec3(20, 20, 20), vec3(0, 0, 1)),
    );
    */



    
    Light lights[3];
    lights[0] = Light(vec3(120, 120, 120), vec3(1, 1, 1) * 0.7);
    lights[1] = Light(vec3(120, -120, 120), vec3(1, 1, 1) * 0.7);
    lights[2] = Light(vec3(-120, 120, -120), vec3(1, 1, 1) * 0.7);
    

    vec3 color = vec3(0, 0, 0);
    for (int i = 0; i < NLIGHT; ++i) {
        color += calcLight(lights[i]);
    }

    //vec3 color = calcLight(lights[0]);

    FragColor = vec4(color, 1.);
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

    # hierarchical
    node_manager.single_mash_mode = False
    obj_dir = os.path.join(os.getcwd(), 'models')

    vertices, normals, indices = load_obj(os.path.join(obj_dir, "b_body.obj"))
    node_manager.append_node("root_body", None, glm.scale(glm.vec3(3,3,3)), glm.vec3(161,194,207) * 0.004, vertices, normals, indices)
    node_manager.append_node("left_body", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(161,194,207) * 0.004, vertices, normals, indices)
    node_manager.append_node("right_body", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(161,194,207) * 0.004, vertices, normals, indices)

    vertices, normals, indices = load_obj(os.path.join(obj_dir, "b_white.obj"))
    node_manager.append_node("root_body_w", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(1,1,1), vertices, normals, indices)
    node_manager.append_node("left_body_w", node_manager.hierarch_nodes["left_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(1,1,1), vertices, normals, indices)
    node_manager.append_node("right_body_w", node_manager.hierarch_nodes["right_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(1,1,1), vertices, normals, indices)
    
    vertices, normals, indices = load_obj(os.path.join(obj_dir, "b_black.obj"))
    node_manager.append_node("root_body_b", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(0, 0, 0), vertices, normals, indices)
    node_manager.append_node("left_body_b", node_manager.hierarch_nodes["left_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(0, 0, 0), vertices, normals, indices)
    node_manager.append_node("right_body_b", node_manager.hierarch_nodes["right_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(0, 0, 0), vertices, normals, indices)
    
    # vertices, normals, indices = load_obj(os.path.join(obj_dir, "body.obj"))
    # node_manager.append_node("root_body", None, glm.scale(glm.vec3(3,3,3)), glm.vec3(161,194,207) * 0.004, vertices, normals, indices)
    # node_manager.append_node("left_body", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(161,194,207) * 0.004, vertices, normals, indices)
    # node_manager.append_node("right_body", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(3,3,3)), glm.vec3(161,194,207) * 0.004, vertices, normals, indices)

    vertices, normals, indices = load_obj(os.path.join(obj_dir, "bolt.obj"))
    node_manager.append_node("root_main_bolt", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(0.3,0.3,0.3)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("root_sub_bolt1", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(0.15,0.15,0.15)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("root_sub_bolt2", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(0.15,0.15,0.15)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    
    node_manager.append_node("left_main_bolt", node_manager.hierarch_nodes["left_body"], glm.scale(glm.vec3(0.3,0.3,0.3)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("left_sub_bolt", node_manager.hierarch_nodes["left_body"], glm.scale(glm.vec3(0.15,0.15,0.15)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)

    node_manager.append_node("right_main_bolt", node_manager.hierarch_nodes["right_body"], glm.scale(glm.vec3(0.3,0.3,0.3)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("right_sub_bolt", node_manager.hierarch_nodes["right_body"], glm.scale(glm.vec3(0.15,0.15,0.15)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)

    vertices, normals, indices = load_obj(os.path.join(obj_dir, "magnet_body.obj"))
    node_manager.append_node("root_left_magnet", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(0.02, 0.02, 0.02)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("root_right_magnet", node_manager.hierarch_nodes["root_body"], glm.scale(glm.vec3(0.02, 0.02, 0.02)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    
    node_manager.append_node("left_left_magnet", node_manager.hierarch_nodes["left_body"], glm.scale(glm.vec3(0.02, 0.02, 0.02)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("left_right_magnet", node_manager.hierarch_nodes["left_body"], glm.scale(glm.vec3(0.02, 0.02, 0.02)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    
    node_manager.append_node("right_left_magnet", node_manager.hierarch_nodes["right_body"], glm.scale(glm.vec3(0.02, 0.02, 0.02)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)
    node_manager.append_node("right_right_magnet", node_manager.hierarch_nodes["right_body"], glm.scale(glm.vec3(0.02, 0.02, 0.02)), glm.vec3(0.7, 0.7, 0.7), vertices, normals, indices)

    vertices, normals, indices = load_obj(os.path.join(obj_dir, "magnet_end_red.obj"))
    node_manager.append_node("root_left_magnet_red", node_manager.hierarch_nodes["root_left_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(0, 0, 1), vertices, normals, indices)
    node_manager.append_node("root_right_magnet_red", node_manager.hierarch_nodes["root_right_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(0, 0, 1), vertices, normals, indices)
    
    node_manager.append_node("left_left_magnet_red", node_manager.hierarch_nodes["left_left_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(0, 0, 1), vertices, normals, indices)
    node_manager.append_node("left_right_magnet_red", node_manager.hierarch_nodes["left_right_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(0, 0, 1), vertices, normals, indices)
    
    node_manager.append_node("right_left_magnet_red", node_manager.hierarch_nodes["right_left_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(0, 0, 1), vertices, normals, indices)
    node_manager.append_node("right_right_magnet_red", node_manager.hierarch_nodes["right_right_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(0, 0, 1), vertices, normals, indices)
    
    vertices, normals, indices = load_obj(os.path.join(obj_dir, "magnet_end_blue.obj"))
    node_manager.append_node("root_left_magnet_blue", node_manager.hierarch_nodes["root_left_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(1, 0, 0), vertices, normals, indices)
    node_manager.append_node("root_right_magnet_blue", node_manager.hierarch_nodes["root_right_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(1, 0, 0), vertices, normals, indices)
    
    node_manager.append_node("left_left_magnet_blue", node_manager.hierarch_nodes["left_left_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(1, 0, 0), vertices, normals, indices)
    node_manager.append_node("left_right_magnet_blue", node_manager.hierarch_nodes["left_right_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(1, 0, 0), vertices, normals, indices)
    
    node_manager.append_node("right_left_magnet_blue", node_manager.hierarch_nodes["right_left_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(1, 0, 0), vertices, normals, indices)
    node_manager.append_node("right_right_magnet_blue", node_manager.hierarch_nodes["right_right_magnet"], glm.scale(glm.vec3(0.02,0.02,0.02)), glm.vec3(1, 0, 0), vertices, normals, indices)
    node_manager.single_mash_mode = True
    
    # debugging frame
    # vertices, normals, indices = load_obj(os.path.join(obj_dir, "bolt.obj"))
    # node_manager.append_node("x", node_manager.hierarch_nodes["root_sub_bolt1"], glm.translate(glm.vec3(5, 0, 0)) * glm.scale(glm.vec3(0.25,0.25,0.25)), glm.vec3(1, 0, 0), vertices, normals, indices)
    # node_manager.append_node("y", node_manager.hierarch_nodes["root_sub_bolt1"], glm.translate(glm.vec3(0, 5 ,0)) * glm.scale(glm.vec3(0.25,0.25,0.25)), glm.vec3(0, 1, 0), vertices, normals, indices)
    # node_manager.append_node("z", node_manager.hierarch_nodes["root_sub_bolt1"], glm.translate(glm.vec3(0, 0, 5)) * glm.scale(glm.vec3(0.25,0.25,0.25)), glm.vec3(0, 0, 1), vertices, normals, indices)

    # loop until the user closes the window
    while not glfwWindowShouldClose(window):
        # render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glClearColor(.5,.5,.5,1)
        # glClearColor(0,0,0,1)
        glEnable(GL_DEPTH_TEST)
        if node_manager.wire_frame_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glUseProgram(shader_color)

        # projection matrix
        P = global_cam.get_projection_matrix()
        # view matrix
        V = global_cam.get_view_matrix()
        view_pos = global_cam.get_eye() + global_cam.pan
        M = glm.mat4()

        # draw grid
        GRID_START = -20
        GRID_END = 21
        GRID_STEP = 1

        glBindVertexArray(vao_grid)
        # X axis of grid
        for i in np.arange(GRID_START, GRID_END, GRID_STEP):
            M = glm.translate(glm.vec3(0, 0, i))
            MVP = P*V*M
            glUniformMatrix4fv(unif_locs_color['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_LINES, 0, 2)

        # Z axis of grid
        for i in np.arange(GRID_START, GRID_END, GRID_STEP):
            M = glm.translate(glm.vec3(i, 0, 0))
            MVP = P*V*M
            glUniformMatrix4fv(unif_locs_color['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_LINES, 2, 2)
          
        t = glfw.get_time();

        glUseProgram(shader_normal)
        glUniform3f(unif_locs_normal['view_pos'], view_pos.x, view_pos.y, view_pos.z)
        
        transforms = {
            # "root": glm.rotate(glm.radians(30 * t), glm.vec3(0, 1, 0)),
            # "root": glm.rotate(0, glm.vec3(0, 1, 0)),
            "root": glm.translate(glm.vec3(0, glm.sin(t*2)/2, 0)) * glm.rotate(glm.radians(t*10), glm.vec3(0, 1, 0)),
            "split": glm.translate(glm.vec3(0, (glm.sin(t)-0.7) * 8 if glm.sin(t)-0.7 > 0 else 0, 0)),
            "self_updown1" :  glm.translate(glm.vec3(0, 4 + (glm.cos(t * 5) + 1) * 0.3, 0)),
            "self_updown2" :  glm.translate(glm.vec3(0, 4 + (glm.sin(t * 5) + 1) * 0.3, 0)),
            "self_rotate_long1": glm.rotate(10 * (glm.cos(t * 5) + 1) * 0.3, glm.vec3(0,1,0)),
            "self_rotate_long2": glm.rotate(10 * (glm.sin(t * 5) + 1) * 0.3, glm.vec3(0,1,0)),
            "self_rotate_short1": glm.rotate(3 * glm.cos(t*2), glm.vec3(0, 1, 0)),
            "self_rotate_short2": glm.rotate(3 * glm.sin(t*2), glm.vec3(0, 1, 0)),
        }
        
        if node_manager.single_mash_mode:
            if node_manager.sigle_node != None:
                node_manager.sigle_node.draw_node(P*V, unif_locs_normal)
        else:
                        
            # node_manager.hierarch_nodes["root_body"].set_transform(glm.translate(glm.vec3(0, 6, 0)) * glm.rotate(glm.radians(30 * t), glm.vec3(0, 1, 0)))
            node_manager.hierarch_nodes["root_body"].set_transform(glm.translate(glm.vec3(0, 6, 0)) * transforms["split"] * transforms["root"])

            node_manager.hierarch_nodes["root_main_bolt"].set_transform(transforms["self_updown1"] * transforms["self_rotate_long1"])
            node_manager.hierarch_nodes["root_sub_bolt1"].set_transform(glm.translate(glm.vec3(-2,-2,-2)) * glm.rotate(glm.radians(-120), glm.vec3(1, 0, -1)) * transforms["self_rotate_short1"])
            node_manager.hierarch_nodes["root_sub_bolt2"].set_transform(glm.translate(glm.vec3(2,-2,-2)) * glm.rotate(glm.radians(-120), glm.vec3(1, 0, 1)) * transforms["self_rotate_short2"])
            node_manager.hierarch_nodes["root_left_magnet"].set_transform(glm.translate(glm.vec3(2.4, 2.4 ,0)) * glm.rotate(-glm.radians(45 + glm.sin(t * 4) * 10), glm.vec3(0, 0, 1)) * (glm.rotate(8 * t, glm.vec3(0,1,0)) if glm.sin(t)-0.7 > 0 else glm.mat4()))
            node_manager.hierarch_nodes["root_right_magnet"].set_transform(glm.translate(glm.vec3(-2.4, 2.4 ,0)) * glm.rotate(glm.radians(180), glm.vec3(0, 1, 0)) * glm.rotate(-glm.radians(45 + glm.sin(t * 4) * 10), glm.vec3(0, 0, 1)) * (glm.rotate(8 * t, glm.vec3(0,1,0)) if glm.sin(t)-0.7 > 0 else glm.mat4()))

            # node_manager.hierarch_nodes["left_body"].set_transform(glm.translate(glm.vec3(4, -4, 0)) * glm.rotate(glm.radians(-120), glm.vec3(0, 0, 1)) * glm.translate(glm.vec3(0, (glm.sin(t)-0.7) * 10 if glm.sin(t)-0.7 > 0 else 0, 0)))
            node_manager.hierarch_nodes["left_body"].set_transform(glm.translate(glm.vec3(4, -4, 0)) * glm.rotate(glm.radians(-120), glm.vec3(0, 0, 1)) * glm.translate(glm.vec3((glm.sin(t)-0.7) * 10 if glm.sin(t)-0.7 > 0 else 0, (glm.sin(t)-0.7) * 10 if glm.sin(t)-0.7 > 0 else 0, 0)))
            node_manager.hierarch_nodes["left_main_bolt"].set_transform(transforms["self_updown2"] * transforms["self_rotate_long2"])
            node_manager.hierarch_nodes["left_sub_bolt"].set_transform(glm.translate(glm.vec3(2,-2,-2)) * glm.rotate(glm.radians(-120), glm.vec3(1, 0, 1)) * transforms["self_rotate_short1"])
            node_manager.hierarch_nodes["left_left_magnet"].set_transform(glm.translate(glm.vec3(2.4, 2.4 ,0)) * glm.rotate(-glm.radians(45 + glm.sin(t * 4) * 10), glm.vec3(0, 0, 1)) * (glm.rotate(8 * t, glm.vec3(0,1,0)) if glm.sin(t)-0.7 > 0 else glm.mat4()))
            node_manager.hierarch_nodes["left_right_magnet"].set_transform(glm.translate(glm.vec3(-2.4, 2.4 ,0)) * glm.rotate(glm.radians(180), glm.vec3(0, 1, 0)) * glm.rotate(-glm.radians(45 + glm.sin(t * 4) * 10), glm.vec3(0, 0, 1)) * (glm.rotate(8 * t, glm.vec3(0,1,0)) if glm.sin(t)-0.7 > 0 else glm.mat4()))


            node_manager.hierarch_nodes["right_body"].set_transform(glm.translate(glm.vec3(-4, -4, 0)) * glm.rotate(glm.radians(120), glm.vec3(0, 0, 1)) * glm.translate(glm.vec3((glm.sin(t)-0.7) * -10 if glm.sin(t)-0.7 > 0 else 0, (glm.sin(t)-0.7) * 10 if glm.sin(t)-0.7 > 0 else 0, 0)))
            node_manager.hierarch_nodes["right_main_bolt"].set_transform(transforms["self_updown2"] * transforms["self_rotate_long2"])            
            node_manager.hierarch_nodes["right_sub_bolt"].set_transform(glm.translate(glm.vec3(-2,-2,-2)) * glm.rotate(glm.radians(-120), glm.vec3(1, 0, -1)) * transforms["self_rotate_short2"])
            node_manager.hierarch_nodes["right_left_magnet"].set_transform(glm.translate(glm.vec3(2.4, 2.4 ,0)) * glm.rotate(-glm.radians(45 + glm.sin(t * 4) * 10), glm.vec3(0, 0, 1)) * (glm.rotate(8 * t, glm.vec3(0,1,0)) if glm.sin(t)-0.7 > 0 else glm.mat4()))
            node_manager.hierarch_nodes["right_right_magnet"].set_transform(glm.translate(glm.vec3(-2.4, 2.4 ,0)) * glm.rotate(glm.radians(180), glm.vec3(0, 1, 0)) * glm.rotate(-glm.radians(45 + glm.sin(t * 4) * 10), glm.vec3(0, 0, 1)) * (glm.rotate(8 * t, glm.vec3(0,1,0)) if glm.sin(t)-0.7 > 0 else glm.mat4()))

            # update
            node_manager.hierarch_nodes["root_body"].update_tree_global_transform()
            for node in node_manager.hierarch_nodes.values():
                node.draw_node(P*V, unif_locs_normal)

        # swap front and back buffers
        glfwSwapBuffers(window)

        # poll events
        glfwPollEvents()

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    main()
