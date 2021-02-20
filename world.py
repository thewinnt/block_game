import chunk

import block_type
import random
import texture_manager

class World:
    def __init__(self):
        self.texture_manager = texture_manager.Texture_manager(16, 16, 256)
        self.block_types = [None]

        self.block_types.append(block_type.block_type(self.texture_manager, "cobblestone", {"all": "cobblestone"})) # create each one of our blocks with the texture manager and a list of textures per face
        self.block_types.append(block_type.block_type(self.texture_manager, "grass", {"top": "grass_block_top", "bottom": "dirt", "sides": "grass_block_side"}))
        self.block_types.append(block_type.block_type(self.texture_manager, "dirt", {"all": "dirt"}))
        self.block_types.append(block_type.block_type(self.texture_manager, "stone", {"all": "stone"}))
        self.block_types.append(block_type.block_type(self.texture_manager, "sand", {"all": "sand"}))
        self.block_types.append(block_type.block_type(self.texture_manager, "oak_planks", {"all": "oak_planks"}))
        self.block_types.append(block_type.block_type(self.texture_manager, "oak_log", {"top": "oak_log_top", "bottom": "oak_log_top", "sides": "oak_log"}))

        self.texture_manager.generate_mipmaps()

        self.chunks = {}
        self.chunks[(0, 0, 0)] = chunk.Chunk(self, (0, 0, 0))

        for x in range(chunk.chunk_width):
            for y in range(chunk.chunk_height):
                for z in range(chunk.chunk_length):
                    self.chunks[(0, 0, 0)].blocks[x][y][z] = random.randint(0, 7)

        self.chunks[(0, 0, 0)].update_mesh()

    def get_block_number(self, pos):
        x, y, z = pos

        chunk_pos = (
            x // chunk.chunk_width,
            y // chunk.chunk_height,
            z // chunk.chunk_length
        )
    
        if not chunk_pos in self.chunks:
            return 0

        bx = int(x % chunk.chunk_width)
        by = y % chunk.chunk_height
        bz = z % chunk.chunk_length

        return self.chunks[chunk_pos].blocks[bx][by][bz]


    def draw(self):
        for chunk_pos in self.chunks:
            self.chunks[chunk_pos].draw()
