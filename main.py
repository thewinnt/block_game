# ======= initialize the stuff =========
# load libraries
from numpy.lib.function_base import blackman
from ursina import *
import random
import ast
import math
import os

game = Ursina()

window.title = 'Block Game v. Alpha 1.0 development version'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.vsync = True
# ======= prepare the variables ========
x = 0
y = 0
z = 0  # camera coordinates
rx = 0
ry = 0  # camera rotation
render_distance = 2
block_types = ["air",
               "stone",
               "grass"] # a list of all the blocks in order, max 256
rendered_blocks_list = [] # a list of all the blocks rendered
chunk_list = []
world_chunks = {}

game_version = "Alpha 1.0 (work in progress)"
# ========= utility functions ==========
def get_block(x, y, z):
    global world_chunks
    if y < 0:
        return '\x00'
    chunkx = str(math.floor(x/16))
    chunkz = str(math.floor(z/16))
    file_name = 'level/chunk_' + chunkx + '_' + chunkz + '.bin'
    try: # try to load from list of loaded chunks
        blocks = world_chunks[file_name][8:]
    except: # if it's not loaded,
        try: # try to load from disk
            with open(file_name, 'r') as chunk_file:
                chunk = chunk_file.read()
        except: # if it doesn't exist, generate it
            print("[DEBUG] Chunk not found:", chunkx, chunkz, ", generating it")
            chunk_file = open(file_name, 'wb+')
            bytex = chunkx.to_bytes(4, byteorder='big', signed=True)
            bytez = chunkz.to_bytes(4, byteorder='big', signed=True)
            blocks = [1] * 256 * 63 # we have 256 blocks in one layer since a chunk is 16x16 blocks and we have 63 of these layers
            blocks += [2] * 256
            blocks += [0] * 256 * 192 # a chunk will be 256 blocks tall
            chunk_file.write(bytex) # write the chunk's x pos
            chunk_file.write(bytez) # write the chunk's z pos
            chunk_file.write(bytearray(blocks)) # write the blocks
        else:
            blocks = chunk[8:]
    x = x % 16
    z = z % 16
    index = y * 256 + z * 16 + x
    try:
        return blocks[index]
    except IndexError:
        return '\x00'
# ========== load the world_chunks ============
def load_world():
    global rendered_blocks_list
    global render_distance
    global block_types
    global x, y, z
    global rx, ry
    global chunk_list
    for chunkx in range(int(x/16) - render_distance, int(x/16) + render_distance):
        for chunkz in range(int(y/16) - render_distance, int(y/16) + render_distance):
            try:
                chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'rb') # open the current chunk
            except:
                print("[DEBUG] Chunk not found:", chunkx, chunkz, ", generating it")
                chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'wb+')
                try:
                    os.mkdir('level')
                except:
                    pass
                bytex = chunkx.to_bytes(4, byteorder='big', signed=True)
                bytez = chunkz.to_bytes(4, byteorder='big', signed=True)
                temp = [1] * 256 * 63 # we have 256 blocks in one layer since a chunk is 16x16 blocks and we have 63 of these layers
                temp += [2] * 256
                temp += [0] * 256 * 192 # a chunk will be 256 blocks tall
                chunk_file.write(bytex) # write the chunk's x pos
                chunk_file.write(bytez) # write the chunk's z pos
                chunk_file.write(bytearray(temp)) # write the blocks
            chunk_file.seek(0, 0)
            temp2 = chunk_file.read()
            chunk_list.append(temp2)
            world_chunks["level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin'] = temp2
            chunk_file.close()
# ========= render the world_chunks ===========
def update_render():
    scene.clear()
    rendered_blocks_list = []
    for i in chunk_list:
        chunkx = 0
        chunkz = 0
        chunkx.from_bytes(i[0:4], byteorder='big', signed=True)
        chunkz.from_bytes(i[4:8], byteorder='big', signed=True)
        k = 0
        for j in i[8:]:
            k += 1
            l = 0
            blockx = chunkx*16 + (k % 16)
            blocky = math.floor(k/256)
            blockz = chunkz*16 + math.floor((k % 256) / 16)
            if block_types[j] != 'air':
                if get_block(blockx - 1, blocky, blockz) == '\x00' or \
                   get_block(blockx + 1, blocky, blockz) == '\x00' or \
                   get_block(blockx, blocky - 1, blockz) == '\x00' or \
                   get_block(blockx, blocky + 1, blockz) == '\x00' or \
                   get_block(blockx, blocky, blockz - 1) == '\x00' or \
                   get_block(blockx, blocky, blockz + 1) == '\x00': # split up for beauty
                    block = Entity(model='cube', color=color.white, scale=(1, 1, 1), texture=block_types[j], world_position=(blockx, blocky, blockz))
                    rendered_blocks_list.append(block)
# ============ game logic ==============
def update():
    if held_keys['w']:
        camera.position += (0, 0, time.dt * 15)
    if held_keys['a']:
        camera.position -= (time.dt * 15, 0, 0)
    if held_keys['s']:
        camera.position -= (0, 0, time.dt * 15)
    if held_keys['d']:
        camera.position += (time.dt * 15, 0, 0)
    if held_keys['shift']:
        camera.position -= (0, time.dt * 15, 0)
    if held_keys['space']:
        camera.position += (0, time.dt * 15, 0)
    if held_keys['left']:
        camera.rotation += (0, 0, time.dt * 15)
    if held_keys['right']:
        camera.rotation -= (time.dt * 15, 0, 0)
    if held_keys['down']:
        camera.rotation -= (0, 0, time.dt * 15)
    if held_keys['up']:
        camera.rotation += (time.dt * 15, 0, 0)
# to be done

# ============== run it! ===============
load_world()
update_render()
game.run()