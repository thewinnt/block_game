# ======= initialize the stuff =========
# load libraries
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

game_version = "Alpha 1.0 (work in progress)"
# ========== load the world ============
def reload_world():
    global rendered_blocks_list
    global render_distance
    global block_types
    global x, y, z
    global rx, ry
    global chunk_list
    scene.clear()
    rendered_blocks_list = []
    for chunkx in range(int(x/16) - render_distance, int(x/16) + render_distance):
        for chunkz in range(int(y/16) - render_distance, int(y/16) + render_distance):
            try:
                chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'rb') # open the current chunk
            except OSError:
                print("[DEBUG] Chunk not found:", chunkx, chunkz, "generating it")
                try:
                    chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'wb+')
                except FileNotFoundError:
                    os.mkdir('level')
                    chunk_file = open("level/chunk_" + str(chunkx) + '_' + str(chunkz) + '.bin', 'wb+')
                bytex = chunkx.to_bytes(4, byteorder='big', signed=True)
                bytez = chunkz.to_bytes(4, byteorder='big', signed=True)
                temp = [1] * 256 * 63 # we have 256 blocks in one layer since a chunk is 16x16 blocks and we have 63 of these layers
                temp += [2] * 256
                temp += [0] * 256 * 192 # a chunk will be 256 blocks tall
                chunk_file.write(bytex) # write the chunk's x pos
                chunk_file.write(bytez) # write the chunk's z pos
                chunk_file.write(bytearray(temp)) # write the blocks
            chunk_file.seek(0, 0)
            chunk_list.append(chunk_file.read())
            chunk_file.close()
# ========= render the world ===========
def render_world():
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
            if not j == '\x00':
                block = Entity(model='cube', color=color.white, scale=(1, 1, 1), texture=block_types[j], world_position=(blockx, blocky, blockz))
                print(k, end=' ')
                rendered_blocks_list.append(block)
# ============ game logic ==============
# to be done

# ============== run it! ===============
reload_world()
game.run()