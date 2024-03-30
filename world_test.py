import pygame
from pygame.locals import *

import eclipse
import eclipse.tile

# Initialize pygame and the display window
pygame.init()
display = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Eclipse Game Engine - World Test")

# Setup Eclipse engine world
world = eclipse.World()
camera = eclipse.Camera()

# Force-fill a couple chunks' surfaces
# so we can see when they're drawn
chunk = world.get_chunk(0, 0, True)
chunk.surface.fill((255, 255, 255))
chunk = world.get_chunk(1, 0, True)
chunk.surface.fill((255, 0, 255))
chunk = world.get_chunk(2, 0, True)
chunk.surface.fill((255, 255, 0))
chunk = world.get_chunk(3, 0, True)
chunk.surface.fill((0, 255, 255))
chunk = world.get_chunk(4, 0, True)
chunk.surface.fill((0, 0, 255))
chunk = world.get_chunk(0, 1, True)
chunk.surface.fill((0, 255, 0))
chunk = world.get_chunk(0, 2, True)
chunk.surface.fill((255, 0, 0))

# Initialize a clock for keeping stable FPS
# and reading deltatime
clock = pygame.time.Clock()

# Initialize main loop running flag
running = True
while running:
    dt = clock.tick(61)/1000

    # Iterate over new pygame events and handle them
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get the keys that are currently being held down
    keys_pressed = pygame.key.get_pressed()
    camera_motion = pygame.Vector2(
        -1 if keys_pressed[K_a] else 1 if keys_pressed[K_d] else 0,
        -1 if keys_pressed[K_w] else 1 if keys_pressed[K_s] else 0)
    camera_motion.clamp_magnitude_ip(1)
    camera.target += camera_motion*700*dt

    # Update the camera
    camera.update(dt)

    # Render content to the display, then update the display
    display.fill((30, 30, 30))
    world.draw(
        surface=display,
        screen_bounds=pygame.Rect((0,0), (1200, 700)),
        camera_position=camera.position)
    pygame.display.flip()

# Close the pygame window and free any left over resources
pygame.quit()