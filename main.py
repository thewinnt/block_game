from ursina import *

game = Ursina()
window.title = 'Block Game v. Pre-'                # The window title
window.borderless = False               # Show a border
window.fullscreen = False               # Do not go Fullscreen
window.exit_button.visible = False      # Do not show the in-game red X that loses the window
window.fps_counter.enabled = True
game.run()