import ctypes

import pyglet.gl as gl

chunk_width = 16
chunk_height = 16
chunk_length = 16

class Chunk:
    def __init__(self, world, chunk_pos):
        self.chunk_pos = chunk_pos

        self.pos = (
            self.chunk_pos[0] * chunk_width,
            self.chunk_pos[1] * chunk_height,
            self.chunk_pos[2] * chunk_length
        )

        self.world = world

        self.blocks = [[[0
            for z in range(chunk_length)]
            for y in range(chunk_height)]
            for x in range(chunk_width)]

        self.has_mesh = False

        self.mesh_vertex_positions = []
        self.mesh_tex_coords = []
        self.mesh_shading_values = []

        self.mesh_index_counter = 0
        self.mesh_indices = []

        self.vao = gl.GLuint(0)
        gl.glGenVertexArrays(1, self.vao)
        gl.glBindVertexArray(self.vao)

        self.vertex_pos_vbo = gl.GLuint(0)
        gl.glGenBuffers(1, self.vertex_pos_vbo)

        self.tex_coord_vbo = gl.GLuint(0)
        gl.glGenBuffers(1, self.tex_coord_vbo)

        self.shading_values_vbo = gl.GLuint(0)
        gl.glGenBuffers(1, self.shading_values_vbo)

        self.ibo = gl.GLuint(0)
        gl.glGenBuffers(1, self.ibo)

    def update_mesh(self):
        self.has_mesh = True

        self.mesh_vertex_positions = []
        self.mesh_tex_coords = []
        self.mesh_shading_values = []

        self.mesh_index_counter = 0
        self.mesh_indices = []

        def add_face(face):
            vertex_positions = block_type.vertex_positions[face].copy()

            for i in range(4):
                vertex_positions[i * 3] += x
                vertex_positions[i * 3 + 1] += y
                vertex_positions[i * 3 + 2] += z

            self.mesh_vertex_positions.extend(vertex_positions)

            indices = [0, 1, 2, 0, 2, 3]

            for i in range(6):
                indices[i] += self.mesh_index_counter

            self.mesh_indices.extend(indices)
            self.mesh_index_counter += 4

            self.mesh_tex_coords.extend(block_type.tex_coords[face])
            self.mesh_shading_values.extend(block_type.shading_values[face])

        for bx in range(chunk_width):
            for by in range(chunk_height):
                for bz in range(chunk_length):
                    block_number = self.blocks[bx][by][bz]

                    if block_number:
                        block_type = self.world.block_types[block_number]
                        x, y, z = (
                            self.pos[0] + bx,
                            self.pos[1] + by,
                            self.pos[2] + bz
                        )

                        if not self.world.get_block_number((x + 1, y, z)): add_face(0)
                        if not self.world.get_block_number((x - 1, y, z)): add_face(1)
                        if not self.world.get_block_number((x, y + 1, z)): add_face(2)
                        if not self.world.get_block_number((x, y - 1, z)): add_face(3)
                        if not self.world.get_block_number((x, y, z + 1)): add_face(4)
                        if not self.world.get_block_number((x, y, z - 1)): add_face(5)

        if not self.mesh_index_counter:
            return

        gl.glBindVertexArray(self.vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_pos_vbo)
        gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.mesh_vertex_positions)),
			(gl.GLfloat * len(self.mesh_vertex_positions)) (*self.mesh_vertex_positions), # use grass block's vertex positions
			gl.GL_STATIC_DRAW)
		
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(0)

		# create tex coord vbo

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_coord_vbo)
        gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.mesh_tex_coords)),
			(gl.GLfloat * len(self.mesh_tex_coords)) (*self.mesh_tex_coords), # use grass block's texture coordinates positions
			gl.GL_STATIC_DRAW)
		
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(1)

        # create shading vbo

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.shading_values_vbo)
        gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.mesh_shading_values)),
			(gl.GLfloat * len(self.mesh_shading_values)) (*self.mesh_shading_values), # use grass block's texture coordinates positions
			gl.GL_STATIC_DRAW)
		
        gl.glVertexAttribPointer(2, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(2)


        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, 
            ctypes.sizeof(gl.GLuint * len(self.mesh_indices)), 
            (gl.GLuint * len(self.mesh_indices)) (*self.mesh_indices), 
            gl.GL_STATIC_DRAW)
    
    def draw(self):
        if not self.mesh_index_counter:
            return

        gl.glBindVertexArray(self.vao)

        gl.glDrawElements(
            gl.GL_TRIANGLES,
            len(self.mesh_indices),
            gl.GL_UNSIGNED_INT,
            None
        )