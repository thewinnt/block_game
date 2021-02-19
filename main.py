# load libraries
import pyglet
import ctypes
import math
pyglet.options["shadow_window"] = False
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
import shader
import matrix
import block_type
import texture_manager

class Window(pyglet.window.Window):
    def __init__(self, **args):
        super().__init__(**args)

        self.texture_manager = texture_manager.Texture_manager(16, 16, 256)

        self.cobblestone = block_type.block_type(self.texture_manager, "cobblestone", {"all": "cobblestone"}) # create each one of our blocks with the texture manager and a list of textures per face
        self.grass = block_type.block_type(self.texture_manager, "grass", {"top": "grass_block_top", "bottom": "dirt", "sides": "grass_block_side"})
        self.dirt = block_type.block_type(self.texture_manager, "dirt", {"all": "dirt"})
        self.stone = block_type.block_type(self.texture_manager, "stone", {"all": "stone"})
        self.sand = block_type.block_type(self.texture_manager, "sand", {"all": "sand"})
        self.oak_planks = block_type.block_type(self.texture_manager, "oak_planks", {"all": "oak_planks"})
        self.oak_log = block_type.block_type(self.texture_manager, "oak_log", {"top": "oak_log_top", "bottom": "oak_log_top", "sides": "oak_log"})

        self.texture_manager.generate_mipmaps()

        self.vao = gl.GLuint(0)
        gl.glGenVertexArrays(1, ctypes.byref(self.vao))
        gl.glBindVertexArray(self.vao)

        # create vertex position vbo

        self.vertex_position_vbo = gl.GLuint(0)
        gl.glGenBuffers(1, ctypes.byref(self.vertex_position_vbo))
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_position_vbo)

        gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.grass.vertex_positions)),
			(gl.GLfloat * len(self.grass.vertex_positions)) (*self.grass.vertex_positions), # use grass block's vertex positions
			gl.GL_STATIC_DRAW)
		
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(0)

		# create tex coord vbo

        self.tex_coord_vbo = gl.GLuint(0)
        gl.glGenBuffers(1, ctypes.byref(self.tex_coord_vbo))
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_coord_vbo)

        gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.grass.tex_coords)),
			(gl.GLfloat * len(self.grass.tex_coords)) (*self.grass.tex_coords), # use grass block's texture coordinates positions
			gl.GL_STATIC_DRAW)
		
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(1)


        self.ibo = gl.GLuint(0)
        gl.glGenBuffers(1, self.ibo)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, 
            ctypes.sizeof(gl.GLuint * len(self.grass.indices)), 
            (gl.GLuint * len(self.grass.indices)) (*self.grass.indices), 
            gl.GL_STATIC_DRAW)

        self.shader = shader.Shader('vert.glsl', 'frag.glsl')
        self.shader_matrix_location = self.shader.find_uniform(b'matrix')
        self.shader_sampler_loaction = self.shader.find_uniform(b'texture_array_sampler')
        self.shader.use()

        self.mv_matrix = matrix.Matrix()
        self.p_matrix = matrix.Matrix()

        self.x = 0
        pyglet.clock.schedule_interval(self.update, 1.0 / 60)

    def update(self, delta_time):
        self.x += delta_time

    def on_draw(self):
        # create projection matrix

        self.p_matrix.load_identity()
        self.p_matrix.perspective(110, float(self.width) / self.height, 0.1, 500)
		
		# create modelview matrix

        self.mv_matrix.load_identity()
        self.mv_matrix.translate(0, 0, -3)
        self.mv_matrix.rotate_2d(self.x, math.sin(self.x / 3 * 2) / 2)

		# modelviewprojection matrix

        mvp_matrix = self.mv_matrix * self.p_matrix
        self.shader.uniform_matrix(self.shader_matrix_location, mvp_matrix)

		# bind textures

        gl.glActiveTexture(gl.GL_TEXTURE0) # set our active texture unit to the first texture unit
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.texture_manager.texture_array) # bind our texture manager's texture
        gl.glUniform1i(self.shader_sampler_loaction, 0) # tell our sampler our texture is bound to the first texture unit

		# draw stuff

        gl.glEnable(gl.GL_DEPTH_TEST) # enable depth testing so faces are drawn in the right order
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.clear()

        gl.glDrawElements(
			gl.GL_TRIANGLES,
			len(self.grass.indices),
			gl.GL_UNSIGNED_INT,
			None)

    def on_resize(self, width, height):
	    print(f"Resize {width} * {height}")
	    gl.glViewport(0, 0, width, height) # resize the actual OpenGL viewport

class Game:
    def __init__(self):
        self.config = gl.Config(double_buffer = True, major_version = 3)
        self.window = Window(config = self.config, width = 800, height = 600, caption ='Block Game v. Pre-Alpha 1.0 development version (attempt 3)', resizable=True, vsync = False)

    def run(self):
        pyglet.app.run()

if __name__ == '__main__':
    game = Game()
    game.run()