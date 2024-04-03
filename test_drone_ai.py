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
tile_test2 = engine.tile_registry.register_tile(
    eclipse.TileRegistryEntry(
        identifier="test2",
        surface=spritesheet.get(pygame.Rect((16, 0), (16, 16)))
    )
)

# Set tiles in the world
chunk = world.get_chunk(0, 0, True)
for x in range(10):
    for y in range(10):
        chunk.set_tile(x, y, eclipse.Tile("test"))



class EnemyDrone(eclipse.Entity):
    sprite: pygame.Surface
    target: t.Union[None, eclipse.Entity] = None

    def __init__(self, *args, **kwargs):
        self.sprite: pygame.Surface = kwargs.get("sprite")
        self.sprite_rect = self.sprite.get_rect()
        del kwargs["sprite"]
        super().__init__(*args, **kwargs)
        self.slipperiness = self.slipperiness_x = self.slipperiness_y = 1
        self.restitution = 0.5
        self.gravity = pygame.Vector2(0, 0)
        self.drag = 0.5
        self.reselect_hover_location()
        self.flight_incentive = random.uniform(0.5, 1.2)
    
    def reselect_hover_location(self):
        self.reselect_hover_location_in = random.uniform(5, 10)
        self.hover_location = pygame.Vector2(
            random.uniform(-64, 64),
            random.uniform(-64, -80)
        )
    
    def on_collision(self, axis: int):
        self.dead = True
    
    def on_death(self):
        # Spawn explosion particles
        for _ in range(random.randint(8, 12)):
            random_1 = random.random()
            self.world.spawn_particle(eclipse.Particle(
                world=self.world,
                position=self.position.copy(),
                velocity=self.velocity.copy()+pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))*25,
                lifetime=random.uniform(3, 5),
                colour=(int(random_1*50+50), int(random_1*50+50), int(random_1*50+50)),
                radius=random.randint(2, 4),
                restitution=random.uniform(0.3, 0.4),
                slipperiness=0.4
            ))
        for _ in range(random.randint(8, 12)):
            random_1 = random.random()
            self.world.spawn_particle(eclipse.Particle(
                world=self.world,
                position=self.position.copy(),
                velocity=self.velocity.copy()+pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))*35,
                lifetime=random.uniform(3, 5),
                colour=(int(random_1*50+130), int(random_1*50+130), int(random_1*50+130)),
                radius=random.randint(2, 4),
                gravity=pygame.Vector2(0, -50),
                drag=random.uniform(0.4, 0.55),
                restitution=0.0,
                slipperiness=0.95
            ))
        for _ in range(random.randint(4, 6)):
            self.world.spawn_particle(eclipse.Particle(
                world=self.world,
                position=self.position.copy(),
                velocity=self.velocity.copy()+pygame.Vector2(random.uniform(-1, 1), random.uniform(-0.5, 0.5))*35,
                lifetime=random.uniform(1, 2),
                colour=(random.uniform(230, 250), random.uniform(165, 190), 90),
                radius=random.randint(1, 2),
                drag=0.3,
                restitution=0.0,
                slipperiness=0.95,
                expire_on_collision=True
            ))
    
    def update(self, dt:float):

        # Get target position and move to it
        if self.target is not None:
            target_position = self.target.position + self.hover_location
            move_distance = (target_position - self.position)*self.flight_incentive
            move_distance.clamp_magnitude_ip(200)
            self.accelerate_to_velocity(move_distance.x, move_distance.y, 4*self.flight_incentive, dt, False)
        
        self.reselect_hover_location_in -= dt
        if self.reselect_hover_location_in < 0:
            self.reselect_hover_location()

        super().update(dt)
    
    def draw(self, surface:pygame.Surface, camera_position:pygame.Vector2):
        center = pygame.Vector2(self.collider_rect.center) - camera_position
        self.sprite_rect.center = center
        surface.blit(self.sprite, self.sprite_rect)

# Create an entity
entity_player = eclipse.Entity(
    world=world,
    position=pygame.Vector2(10, -10),
    collider_size=pygame.Vector2(14, 30)
)
world.entities.append(entity_player)

drone_spritesheet = eclipse.Spritesheet("./assets/drone.png")
drone_sprite = drone_spritesheet.get(pygame.Rect(0, 0, 18, 18))

# Initialize a clock for keeping stable FPS
# and reading deltatime
clock = pygame.time.Clock()

# Initialize main loop running flag
running = True
while running:
    dt = clock.tick(145)/1000

    keydown_events = {}

    # Iterate over new pygame events and handle them
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            keydown_events[event.key] = 1

            if event.key == pygame.K_r:
                _ = EnemyDrone(
                    world=world,
                    position=pygame.Vector2(50, -10),
                    collider_size=pygame.Vector2(14, 14),
                    sprite=drone_sprite )
                _.target = entity_player
                world.entities.append(_)
    
    # Get the keys that are currently being held down
    keys_pressed = pygame.key.get_pressed()
    engine.camera.target = entity_player.get_rect_position() - pygame.Vector2(screen_size[0]/2, screen_size[1]/2)

    entity_player.update_movement(
        move_left=keys_pressed[K_a],
        move_right=keys_pressed[K_d],
        jump=keydown_events.get(K_w, 0),
        acceleration=7,
        acceleration_air=1,
        movement_speed=120,
        jump_force=200,
        dt=dt
    )

    # Update the camera
    engine.camera.update(dt)

    # Update the world
    world.update(dt)
    
    # Get, then convert mouse pos to world pos
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    mouse_pos_world = engine.screen_space_to_world_space(mouse_pos, display_scale)
    
    # Place bricks
    if keys_pressed[K_b]:
        chunk_x, chunk_y = world.world_location_to_chunk_location(mouse_pos_world.x, mouse_pos_world.y)
        chunk:eclipse.chunk.Chunk = world.get_chunk(chunk_x, chunk_y, True)
        if chunk is not None:
            tile_x, tile_y = chunk.chunk_location_to_tile_location(
                mouse_pos_world.x%256,
                mouse_pos_world.y%256)
            tile = chunk.get_tile(tile_x, tile_y)
            chunk.set_tile(tile_x, tile_y, eclipse.Tile("test" if not keys_pressed[K_2] else "test2"))

    # Render content to the display, then update the display
    screen.fill((30, 30, 30))
    world.draw(
        surface=screen,
        screen_bounds=pygame.Rect((0,0), screen_size),
        camera_position=engine.camera.position.__floordiv__(1))
    display.blit(pygame.transform.scale(screen, display_size), (0,0))

    pygame.display.flip()

# Close the pygame window and free any left over resources
pygame.quit()