# load libraries
import pyglet
import math
pyglet.options["shadow_window"] = False
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
import shader
import camera
import world

class Window(pyglet.window.Window):
    def __init__(self, **args):
        super().__init__(**args)

        self.world = world.World()

        self.shader = shader.Shader('vert.glsl', 'frag.glsl')
        self.shader_sampler_loaction = self.shader.find_uniform(b'texture_array_sampler')
        self.shader.use()

        pyglet.clock.schedule_interval(self.update, 1/2**31)
        self.mouse_captured = False

        self.camera = camera.Camera(self.shader, self.width, self.height)

    def update(self, dt):
        if not self.mouse_captured:
            self.camera.input = [0, 0, 0]
        self.camera.update_camera(dt)
        print(f'FPS: {round(1.0/dt)}', end='')

    def on_draw(self):
        self.camera.update_martices()

		# bind textures

        gl.glActiveTexture(gl.GL_TEXTURE0) # set our active texture unit to the first texture unit
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.world.texture_manager.texture_array) # bind our texture manager's texture
        gl.glUniform1i(self.shader_sampler_loaction, 0) # tell our sampler our texture is bound to the first texture unit

		# draw stuff
        
        gl.glEnable(gl.GL_DEPTH_TEST) # enable depth testing so faces are drawn in the right order
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glClearColor(0.3, 0.6, 0.7, 1.0)
        self.clear()
        self.world.draw()

    def on_resize(self, width, height):
        print(f"Resize {width} * {height}")
        gl.glViewport(0, 0, width, height)
        self.camera.width = width
        self.camera.height = height

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_captured = not self.mouse_captured
        self.set_exclusive_mouse(self.mouse_captured)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_captured:
            sensitivity = 0.004
            self.camera.rotation[0] -= dx * sensitivity
            self.camera.rotation[1] += dy * sensitivity

            self.camera.rotation[1] = max(-math.tau / 4, min(math.tau / 4, self.camera.rotation[1]))

    def on_key_press(self, key, modifiers):
        if not self.mouse_captured:
            return

        if   key == pyglet.window.key.D: self.camera.input[0] += 1
        elif key == pyglet.window.key.A: self.camera.input[0] -= 1
        elif key == pyglet.window.key.W: self.camera.input[2] += 1
        elif key == pyglet.window.key.S: self.camera.input[2] -= 1

        elif key == pyglet.window.key.SPACE : self.camera.input[1] += 1
        elif key == pyglet.window.key.LSHIFT: self.camera.input[1] -= 1
	
    def on_key_release(self, key, modifiers):
        if not self.mouse_captured:
            return

        if   key == pyglet.window.key.D: self.camera.input[0] -= 1
        elif key == pyglet.window.key.A: self.camera.input[0] += 1
        elif key == pyglet.window.key.W: self.camera.input[2] -= 1
        elif key == pyglet.window.key.S: self.camera.input[2] += 1

        elif key == pyglet.window.key.SPACE : self.camera.input[1] -= 1
        elif key == pyglet.window.key.LSHIFT: self.camera.input[1] += 1

class Game:
    def __init__(self):
        self.config = gl.Config(double_buffer = True, major_version = 3, depth_size = 16)
        self.window = Window(config = self.config, width = 800, height = 600, caption ='Block Game v. Pre-Alpha 1.0 development version (attempt 3)', resizable=True, vsync = False)
        

    def run(self):
        pyglet.app.run()

if __name__ == '__main__':
    game = Game()
    game.run()