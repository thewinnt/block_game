from ursina import *
import random

random_generator = random.Random()
texoffset = 0.0                         # define a variable that will keep the texture offset
texoffset2 = 0.0

game = Ursina()

window.title = 'Block Game v. Training Test (for educational purposes)'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.vsync = True

Text.size = 0.05
Text.default_resolution = 1080 * Text.size
info = Text(text="A powerful waterfall roaring on the mountains")
info.x = -0.5
info.y = 0.4
info.background = True
info.visible = False  

cubes = []                                          # Create the list
cube = Entity(model='cube', color=color.orange, scale=(2,2,2), texture="assets/white_wool")
cubes.append(cube)
cube2 = Entity(model='cube', color=color.rgba(255,255,255,128), scale=(2.5,2.5,2.5), texture="assets/white_wool")
cubes.append(cube2) 

def input(key):
    if key == 'z':
        red = random_generator.random() * 255
        green = random_generator.random() * 255
        blue = random_generator.random() * 255
        cube.color = color.rgb(red, green, blue)   # Note I still can reference any individual object I want

    if key == 'c':
        x = random_generator.random() * 10 - 5     # Value between -5 and 5
        y = random_generator.random() * 10 - 5     # Value between -5 and 5
        z = random_generator.random() * 10 - 5     # Value between -5 and 5
        s = random_generator.random() * 1          # Scale between 0 and 1
        # Create the new cube and add it to the list
        red = random_generator.random() * 255
        green = random_generator.random() * 255
        blue = random_generator.random() * 255
        newcube = Entity(parent=cube, model='cube', color=color.rgb(red, green, blue), position=(x, y, z), scale=(s,s,s), texture="assets/grass_block_top")
        newcube.color = color.rgb(red, green, blue)
        cubes.append(newcube)

        # Create another child cube and add it to the list but using the newcube as the parent, keep the same colour, make it smaller
        childcube = Entity(parent=newcube, model='cube', color=color.rgb(red, green, blue), position=(1, 0, 0), scale=(s/2, s/2, s/2), texture="assets/grass_block_top")
        cubes.append(childcube)

def update():
    for entity in cubes:                             # Go through the cube list
        entity.rotation_y += time.dt * 50
    if held_keys['t']:
        print(held_keys['t'])
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
    
    global texoffset                                 # Inform we are going to use the variable defined outside
    global texoffset2                                 # Inform we are going to use the variable defined outside
    texoffset += time.dt * 0.2                       # Add a small number to this variable
    setattr(cube, "texture_offset", (texoffset, 0))  # Assign as a texture offset
    texoffset2 += time.dt * 0.3                       # Add a small number to this variable
    setattr(cube2, "texture_offset", (texoffset2, 0))  # Assign as a texture offset

    if mouse.hovered_entity == cube:                 # If the mouse is hovering over the cube entity
        info.visible = True                          # Make the text visible
    else:                                            # else
        info.visible = False                         # hide it again

game.run()