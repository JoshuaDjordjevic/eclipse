import math
import random
import typing as t
import pygame
from pygame.locals import *

import eclipse
import eclipse.chunk
from eclipse.entity import drag_default, gravity_default, restitution_default, slipperiness_default

# Initialize pygame and the display window
pygame.init()
display_scale = 2
display_size = (1200, 700)
screen_size = (display_size[0]//display_scale, display_size[1]//display_scale)
display = pygame.display.set_mode(display_size)
screen = pygame.Surface(screen_size)
pygame.display.set_caption("Eclipse Game Engine - Entity Test")

# Setup Eclipse engine world
engine = eclipse.Engine()
world = engine.create_new_world("world")

# Center the camera position
engine.camera.target.x -= screen_size[0]/2 - 16*5
engine.camera.target.y -= screen_size[1]/2 - 16*5
engine.camera.position.x = engine.camera.target.x
engine.camera.position.y = engine.camera.target.y
engine.camera.snap = 10

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


# Custom entity class called Drone
class Drone(eclipse.Entity):
    def __init__(self, world: eclipse.World, position: pygame.Vector2, collider_size: pygame.Vector2, gravity: pygame.Vector2 = ..., drag=..., restitution=..., slipperiness=...):
        super().__init__(world, position, collider_size, gravity, drag, restitution, slipperiness)
        self.rotation = 0.0
        self.rotational_velocity = 0
        self.rotational_drag = 0.4
        self.rotational_velocity_max = 25
    
    def draw(self, surface: pygame.Surface, camera_position: ...) -> None:
        # Draw direction line
        pygame.draw.line(
            surface,
            (127, 255, 127),
            (   self.collider_rect.centerx-camera_position.x,
                self.collider_rect.centery-camera_position.y ),
            (   self.collider_rect.centerx-camera_position.x+math.cos(self.rotation)*15,
                self.collider_rect.centery-camera_position.y+math.sin(self.rotation)*15 ),
            1
        )
        super().draw(surface, camera_position)

    def on_collision(self, axis: int):
        sign = 1
        normal_sign = 1 if self.velocity[axis]>0 else 0
        if normal_sign != axis: sign = -1
        perpendicular_force = self.velocity[1-axis]
        self.rotational_velocity += perpendicular_force * 0.05 * abs(self.velocity[axis]*0.01) * sign
        return super().on_collision(axis)

    def update(self, dt: ...):
        super().update(dt)
        self.rotation += self.rotational_velocity*dt
        self.rotational_velocity -= self.rotational_velocity*self.rotational_drag*dt
        self.rotational_velocity = min(max(self.rotational_velocity, -self.rotational_velocity_max), self.rotational_velocity_max)


# Create an entity
e = Drone(
    world=world,
    position=pygame.Vector2(10, -10),
    collider_size=pygame.Vector2(24, 24)
)
e.velocity.x = 20
e.gravity = pygame.Vector2(0, 0)
e.restitution = 0.45
e.slipperiness = 0.99
e.drag = 1.5
world.entities.append(e)

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
    engine.camera.target = e.get_rect_position() - pygame.Vector2(screen_size[0]/2, screen_size[1]/2)

    keyboard_input_vector = pygame.Vector2(
        -1 if keys_pressed[K_a] else 1 if keys_pressed[K_d] else 0,
        -1 if keys_pressed[K_w] else 1 if keys_pressed[K_s] else 0)
    keyboard_input_vector.clamp_magnitude_ip(1)

    e.velocity += keyboard_input_vector*250*dt

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