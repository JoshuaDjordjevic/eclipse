import random
import pygame
from pygame.locals import *

import eclipse
import eclipse.chunk

# Initialize pygame and the display window
pygame.init()
display_scale = 2
display_size = (1200, 700)
screen_size = (display_size[0]//display_scale, display_size[1]//display_scale)
display = pygame.display.set_mode(display_size)
screen = pygame.Surface(screen_size)
pygame.display.set_caption("Eclipse Game Engine - World Test")

# Setup Eclipse engine world
engine = eclipse.Engine()
world = engine.create_new_world("world")

# Center the camera position
engine.camera.target.x -= screen_size[0]/2 - 16*5
engine.camera.target.y -= screen_size[1]/2 - 16*5
engine.camera.position.x = engine.camera.target.x
engine.camera.position.y = engine.camera.target.y

# Setup spritesheet
spritesheet = eclipse.Spritesheet("./assets/tiles.png")

# Register tiles
tile_test = engine.tile_registry.register_tile(
    eclipse.TileRegistryEntry(
        identifier="test",
        surface=spritesheet.get(pygame.Rect((0, 0), (16, 16)))
    )
)

# Set tiles in the world
chunk = world.get_chunk(0, 0, True)
for x in range(10):
    for y in range(10):
        chunk.set_tile(x, y, eclipse.Tile("test"))

# Initialize a clock for keeping stable FPS
# and reading deltatime
clock = pygame.time.Clock()

# Initialize main loop running flag
running = True
while running:
    dt = clock.tick(145)/1000

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
    engine.camera.target += camera_motion*300*dt

    # Update the camera
    engine.camera.update(dt)

    # Update the world
    world.update(dt)
    
    # Get, then convert mouse pos to world pos
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    mouse_pos_world = engine.screen_space_to_world_space(mouse_pos, display_scale)

    # Spawn particles
    if keys_pressed[K_p]:
        c = random.randint(127, 255)
        particle = eclipse.Particle(
            world=world,
            position=mouse_pos_world,
            velocity=pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))*80,
            lifetime=15.0,
            colour=(c, 255-c, random.randint(0, 255)),
            radius=2)
        world.particles.append(particle)
    
    # Place bricks
    if keys_pressed[K_b]:
        chunk_x, chunk_y = world.world_location_to_chunk_location(mouse_pos_world.x, mouse_pos_world.y)
        chunk:eclipse.chunk.Chunk = world.get_chunk(chunk_x, chunk_y, True)
        if chunk is not None:
            tile_x, tile_y = chunk.chunk_location_to_tile_location(
                mouse_pos_world.x%256,
                mouse_pos_world.y%256)
            tile = chunk.get_tile(tile_x, tile_y)
            if tile is None:
                chunk.set_tile(tile_x, tile_y, eclipse.Tile("test"))

    # Render content to the display, then update the display
    screen.fill((30, 30, 30))
    world.draw(
        surface=screen,
        screen_bounds=pygame.Rect((0,0), screen_size),
        camera_position=engine.camera.position.__floordiv__(1))
    display.blit(pygame.transform.scale(screen, display_size), (0,0))

    # Rect at mouse for collision testing
    r = pygame.Rect((0,0), (50, 50))
    r.center = mouse_pos_world

    r_collided = world.collide_rect(r)

    r_screenspace = engine.world_space_rect_to_screen_space_rect(r, display_scale)
    pygame.draw.rect(display,
                     (255, 255, 255) if r_collided else (127, 127, 127),
                     r_screenspace, 2)

    # Draw a circle around the mouse cursor
    pygame.draw.circle(
        display,
        (255, 255, 127) if not world.collide_point(mouse_pos_world) else (255, 127, 127),
        engine.world_space_to_screen_space(mouse_pos_world, display_scale),
        16, 2)

    pygame.display.flip()

# Close the pygame window and free any left over resources
pygame.quit()