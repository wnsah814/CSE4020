from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

def prepare_vao_triangle():
    # prepare vertex data (in main memory)
    vertices = glm.array(glm.float32,
        # position        # color
        0.0, 0.0, 0.0,  1.0, 0.0, 0.0, # v0
        0.5, 0.0, 0.0,  0.0, 1.0, 0.0, # v1
        0.0, 0.5, 0.0,  0.0, 0.0, 1.0, # v2
    )

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def prepare_vao_frame():
    # prepare vertex data (in main memory)
    vertices = glm.array(glm.float32,
        # position        # color
        0.0, 0.0, 0.0,  1.0, 0.0, 0.0, # x-axis start
        10.0, 0.0, 0.0,  1.0, 0.0, 0.0, # x-axis end 
        0.0, 0.0, 0.0,  0.0, 1.0, 0.0, # y-axis start
        0.0, 10.0, 0.0,  0.0, 1.0, 0.0, # y-axis end 
        0.0, 0.0, 0.0,  0.0, 0.0, 1.0, # z-axis start
        0.0, 0.0, 10.0,  0.0, 0.0, 1.0, # z-axis end 
    )

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def prepare_vao_grid():
    # prepare vertex data (in main memory)
    # vertices = glm.array()

    # foi in np.arange(-10, 10, 0.5):
    #     vertices.
    vertices = glm.array(glm.float32,
        # position        # color
        -10.0, 0.0, 0.0,  1.0, 1.0, 1.0, # x-axis start
        10.0, 0.0, 0.0,  1.0, 1.0, 1.0, # x-axis end 
        0.0, 0.0, -10.0,  1.0, 1.0, 1.0, # z-axis start
        0.0, 0.0, 10.0,  1.0, 1.0, 1.0, # z-axis end 
    )

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def prepare_vao_cube():
    vertices = glm.array(glm.float32,
        0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 1.0, 1.0, 0.0, 0.0,
        
        0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
        1.0, 1.0, 0.0, 0.0, 1.0, 0.0,
        0.0, 1.0, 1.0, 0.0, 1.0, 0.0,
        1.0, 1.0, 1.0, 0.0, 1.0, 0.0,
        
        0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 0.0, 1.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 1.0, 0.0, 0.0,
        
        0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
        0.0, 1.0, 1.0, 1.0, 0.0, 0.0,

        1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 0.0, 1.0, 0.0, 0.0,

        0.0, 0.0, 1.0, 1.0, 0.0, 0.0,
        0.0, 1.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 1.0, 1.0, 0.0, 0.0,

    )
 
    # indices = [0, 1, 2, 2, 3, 0,
    #            4, 5, 6, 6, 7, 4,
    #            4, 5, 1, 1, 0, 4,
    #            6, 7, 3, 3, 2, 6,
    #            5, 6, 2, 2, 1, 5,
    #            7, 4, 0, 0, 3, 7]
 
    # indices = np.array(indices, dtype = np.uint32)

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO
