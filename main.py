# load libraries
from pyglet.gl import *
from pyglet.window import key
import math
import os
# ======= prepare the variables ========
world_chunks = {} # a list of the loaded chunks
render_distance = 1
block_types = ["air",
               "stone",
               "grass"] # a list of all the blocks in order, max 256
player_coordinates = [0.0, 64.0, 0.0] # player's coordinates, all the coordinates are relative to world center
player_rotation = [0.0, 0.0] # player's rotation
chunk_list = []
# ========= utility functions ==========
def get_block(x, y, z):
    global world_chunks
    if y < 0:
        return 69420 # that block is outside of the world anyways, it won't be rendered
    elif y > 255:
        return 0 # we should definitely see the top face of a block that 100% doesn't have anything above it
    chunkx = str(math.floor(x/16))
    chunkz = str(math.floor(z/16))
    file_name = 'level/chunk_' + chunkx + '_' + chunkz + '.bin'
    try:
        blocks = world_chunks[file_name][8:]
    except:
        return 69420
    x = x % 16
    z = z % 16
    index = y * 256 + z * 16 + x
    return blocks[index]
# ========== load the world ============
def load_world():
    global render_distance
    global block_types
    global player_coordinates
    global chunk_list
    chunk_list = []
    for chunkx in range(int(player_coordinates[0]/16) - render_distance, int(player_coordinates[0]/16) + render_distance):
        for chunkz in range(int(player_coordinates[2]/16) - render_distance, int(player_coordinates[2]/16) + render_distance):
            try:
                chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'rb') # open the current chunk
            except:
                print("[DEBUG] Chunk not found:", chunkx, chunkz, ", generating it")
                try:
                    os.mkdir('level')
                except:
                    pass
                chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'wb+')
                bytex = chunkx.to_bytes(4, byteorder='big', signed=True)
                bytez = chunkz.to_bytes(4, byteorder='big', signed=True)
                temp = [1] * 256 * 63 # we have 256 blocks in one layer since a chunk is 16x16 blocks and we have 63 of these layers
                temp += [2] * 256
                temp += [0] * 256 * 191 # a chunk will be 256 blocks tall
                temp += [1] * 256
                chunk_file.write(bytex) # write the chunk's x pos
                chunk_file.write(bytez) # write the chunk's z pos
                chunk_file.write(bytearray(temp)) # write the blocks
            chunk_file.seek(0, 0)
            temp2 = chunk_file.read()
            world_chunks["level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin'] = temp2
            chunk_list.append(temp2)
            chunk_file.close()
# ======= try to make it render ========
class Model(): # the actual thing that renders, i guess
    def get_tex(self, file):
        tex = pyglet.image.load(file).get_texture()
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)
    
    def reload_world(self): # reload the world everytime something changes. i can't think of anything that would work better.
        load_world()
        # please forgive me. or, even better, help me make something more optimized
        self.batch = pyglet.graphics.Batch()
        for i in chunk_list: # for each chunk
            chunkx = 0 # determine its posotion
            chunkz = 0
            chunkx = int.from_bytes(i[0:4], byteorder='big', signed=True)
            chunkz = int.from_bytes(i[4:8], byteorder='big', signed=True)
            print('[DEBUG] Chunk', chunkx, chunkz)
            k = -1
            for j in i[8:]: # then for each block in that chunk
                k += 1      # add it to the batch if is surrounded by air on at least one side
                if j != 0:
                    bx = chunkx*16 + (k % 16)
                    by = k//256
                    bz = chunkz*16 + (k % 256) // 16
                    tex_coords = ('t2i', (0,0, 1,0, 1,1, 0,1))
                    if get_block(bx-1, by, bz) == 0:
                        self.batch.add(4, GL_QUADS, self.textures[block_types[j]]['side'], ('v3i', (bx,by,bz, bx,by,bz+1, bx,by+1,bz+1, bx,by+1,bz)), tex_coords)
                    if get_block(bx+1, by, bz) == 0:
                        self.batch.add(4, GL_QUADS, self.textures[block_types[j]]['side'], ('v3i', (bx+1,by,bz+1, bx+1,by,bz, bx+1,by+1,bz, bx+1,by+1,bz+1)), tex_coords)
                    if get_block(bx, by, bz-1) == 0:
                        self.batch.add(4, GL_QUADS, self.textures[block_types[j]]['side'], ('v3i', (bx+1,by,bz, bx,by,bz, bx,by+1,bz, bx+1,by+1,bz)), tex_coords)
                    if get_block(bx, by, bz+1) == 0:
                        self.batch.add(4, GL_QUADS, self.textures[block_types[j]]['side'], ('v3i', (bx,by,bz+1, bx+1,by,bz+1, bx+1,by+1,bz+1, bx,by+1,bz+1)), tex_coords)
                    if get_block(bx, by-1, bz) == 0:
                        self.batch.add(4, GL_QUADS, self.textures[block_types[j]]['bottom'], ('v3i', (bx,by,bz, bx+1,by,bz, bx+1,by,bz+1, bx,by,bz+1)), tex_coords)
                    if get_block(bx, by+1, bz) == 0:
                        self.batch.add(4, GL_QUADS, self.textures[block_types[j]]['top'], ('v3i', (bx,by+1,bz+1, bx+1,by+1,bz+1, bx+1,by+1,bz, bx,by+1,bz)), tex_coords)

    def __init__(self, reload = False):
        self.textures = {}
        for i in block_types:
            if i != 'air':
                self.textures[i] = {}
                self.textures[i]['top'] = self.get_tex('assets/textures/block/top/' + i + '.png')
                self.textures[i]['side'] = self.get_tex('assets/textures/block/side/' + i + '.png')
                self.textures[i]['bottom'] = self.get_tex('assets/textures/block/bottom/' + i + '.png')
        self.batch = pyglet.graphics.Batch()
        if reload:
            self.reload_world()

    def draw(self):
        self.batch.draw()

class Player(): # that's just the player who plays the game and creates world updates, etc.
    def __init__(self, pos = (0, 64, 0), rot = (0, 0)):
        self.pos = list(pos)
        self.rot = list(rot)
        self.model = Model()

    def mouse_motion(self, dx, dy):
        dx /= 8
        dy /= 8
        self.rot[0] += dy
        self.rot[1] -= dx
        if self.rot[0] > 90:
            self.rot[0] = 90
        elif self.rot[0] < -90:
            self.rot[0] = -90

    def update(self, dt, keys):
        s = dt*10
        rot_y = -self.rot[1] / 180 * math.pi
        dx, dz = s*math.sin(rot_y), s*math.cos(rot_y)
        old_chunk = [self.pos[0] // 16, self.pos[2] // 16]
        if keys[key.W]:
            self.pos[0] += dx
            self.pos[2] -= dz
        if keys[key.A]:
            self.pos[0] -= dz
            self.pos[2] -= dx
        if keys[key.S]:
            self.pos[0] -= dx
            self.pos[2] += dz
        if keys[key.D]:
            self.pos[0] += dz
            self.pos[2] += dx
        if keys[key.SPACE]:
            self.pos[1] += s
        if keys[key.LSHIFT]:
            self.pos[1] -= s
        new_chunk = [self.pos[0] // 16, self.pos[2] // 16]
        if old_chunk != new_chunk:
            self.model.reload_world()

class Window(pyglet.window.Window): # the window
    def push(self, pos, rot):
        glPushMatrix()
        rot = self.player.rot
        glRotatef(-rot[0], 1, 0, 0)
        glRotatef(-rot[1], 0, 1, 0)
        glTranslatef(-pos[0], -pos[1], -pos[2])

    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()

    def set2d(self):
        self.Projection()
        gluOrtho2D(0, self.width, 0, self.height)
        self.Model()

    def set3d(self):
        self.Projection()
        gluPerspective(110, self.width/self.height, 0.05, 1000)
        self.Model()
    
    def setLock(self, state):
        self.lock = state
        self.set_exclusive_mouse(state)
    lock = False
    mouse_lock = property(lambda self:self.lock, setLock)

    def __init__(self, *args, **kwargs):
        global player_coordinates
        global player_rotation
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 150)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.model = Model(True)
        self.player = Player(player_coordinates, player_rotation)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_lock:
            self.player.mouse_motion(dx, dy)

    def on_key_press(self, KEY, MOD):
        if KEY == key.P: # because escape is too easy to accidentally press
            self.close()
        elif KEY == key.C:
            self.mouse_lock = not self.mouse_lock
        elif KEY == key.Z:
            print(self.player.pos, self.player.rot)
    
    def update(self, dt):
        self.player.update(dt, self.keys)

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos, self.player.rot)
        self.model.draw()
        glPopMatrix()

# ============== rut it! ===============
if __name__ == '__main__': # the actual code that starts the game
    window = Window(width=960, height=640, caption ='Block Game v. Pre-Alpha 1.0 development version', resizable=True)
    glClearColor(0.5, 0.7, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE) # this little line optimizes the game by a ton by making the invisible blocks not render at all
                           # hopefully its effect will be visible
    pyglet.app.run()