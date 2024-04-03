import typing as t

import pygame

from eclipse import util
from .chunk import Chunk
from .tile import TileRegistry
from .particle import Particle
from .entity import Entity

class ChunkGenerator(object):
    def __init__(self):
        ...
    
    def create_chunk(self, x:int, y:int):
        return Chunk(None)

class World(object):
    chunks:t.Dict[str, Chunk]
    chunk_generator:ChunkGenerator
    tile_registry: TileRegistry
    particles:t.List[Particle]
    entities:t.List[Entity]
    _last_chunks_drawn_count:int

    def __init__(self, tile_registry:TileRegistry):
        self.chunks = {}
        self.chunk_generator = ChunkGenerator()
        self.tile_registry = tile_registry
        self.particles = []
        self.entities = []
    
    def get_chunk_key(self, x:int, y:int) -> str:
        return f"w{x},{y}"
    
    def get_chunk(self, x:int, y:int, create_if_not_exists:bool=False):
        key = self.get_chunk_key(x, y)
        chunk = self.chunks.get(key)
        if chunk is None and create_if_not_exists:
            chunk = self.chunk_generator.create_chunk(x, y)
            chunk.tile_registry = self.tile_registry
            self.chunks[key] = chunk
        return chunk

    def world_location_to_chunk_location(
            self, x:float, y:float) -> t.Tuple[int, int]:
        """Converts a given world location into a chunk location.

        Args:
            x (float): X location in the world.
            y (float): Y location in the world.

        Returns:
            (x (int), y (int)): The chunk location.
        """
        return ( int(x//256),
                 int(y//256) )
    
    # Needs point and rect collision functions
    # Check tiles that intersect
    # Check tile colliders

    def collide_point(self, point:pygame.Vector2) -> bool:
        """Checks if a given point in the world collides
        with any tiles.

        Args:
            point (pygame.Vector2): The point in world space.

        Returns:
            bool: Whether the point collided.
        """
        chunk_x, chunk_y = self.world_location_to_chunk_location(point.x, point.y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        if chunk is None:
            return False
        # Convert the point to chunk-space and check
        # whether it collides in the chunk
        point_chunkspace = pygame.Vector2(
            point.x%256,
            point.y%256)
        return chunk.collide_point(point_chunkspace)
    
    def collide_rect(self, rect:pygame.Rect) -> bool:
        tile_min = (
            rect.left//16,
            rect.top//16)
        tile_max = (
            util.ceil_div(rect.right, 16),
            util.ceil_div(rect.bottom, 16))
        for y in range(tile_min[1], tile_max[1]):
            for x in range(tile_min[0], tile_max[0]):
                # Get the chunk at this tile location
                chunk_x = x//16
                chunk_y = y//16
                chunk = self.get_chunk(chunk_x, chunk_y)
                if chunk is None:
                    continue
                # Get the tile at this location
                tile_space_x = x%16
                tile_space_y = y%16
                tile = chunk.get_tile(tile_space_x, tile_space_y)
                if tile is None:
                    continue
                # Get the tile registry entry to find collisions
                tile_registry_entry = self.tile_registry.get_tile_registry_entry(tile.identifier)
                if tile_registry_entry is None:
                    continue
                # print(f"Test collision at {x}, {y}")
                if tile_registry_entry.collide_rect(rect, pygame.Vector2(x*16, y*16)):
                    return True
        return False

    def update(self, dt:float):
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        for entity in self.entities:
            entity.update(dt)
    
    def spawn_particle(self, particle:Particle):
        self.particles.append(particle)
    
    def draw_chunks(self,
                    surface:pygame.Surface,
                    screen_bounds:pygame.Rect,
                    camera_position:pygame.Vector2):
        # Convert screen bounds to world coordinates
        screen_bounds_min = screen_bounds.topleft
        screen_bounds_max = screen_bounds.bottomright
        world_bounds_min = (
            screen_bounds_min[0]+camera_position.x,
            screen_bounds_min[1]+camera_position.y )
        world_bounds_max = (
            screen_bounds_max[0]+camera_position.x,
            screen_bounds_max[1]+camera_position.y )
        # Find the min and max chunks we need to draw
        chunk_min = self.world_location_to_chunk_location(*world_bounds_min)
        chunk_max = self.world_location_to_chunk_location(*world_bounds_max)
        # Initialize chunk draw counter
        chunk_draw_counter = 0
        # Iterate over the chunk range to draw visible chunks
        for y in range(chunk_min[1], chunk_max[1]+1):
            for x in range(chunk_min[0], chunk_max[0]+1):
                chunk = self.get_chunk(x, y, False)
                if chunk is None: continue
                # Floor pixel coordinates to fix odd offset rendering bug
                pixel_x = (x*256 - camera_position.x) // 1
                pixel_y = (y*256 - camera_position.y) // 1
                surface.blit(chunk.surface, (pixel_x, pixel_y))
                # Increment chunk draw counter
                chunk_draw_counter += 1
        # Update the last chunks drawn count
        self._last_chunks_drawn_count = chunk_draw_counter

    def draw_entities(self,
                      surface:pygame.Surface,
                      camera_position:pygame.Vector2):
        remove_entities = []
        for e in self.entities:
            e.draw(surface, camera_position)
            if e.dead:
                e.on_death()
                e.on_despawn()
                remove_entities.append(e)
            elif e.despawn:
                e.on_despawn()
                remove_entities.append(e)
        for e in remove_entities:
            self.entities.remove(e)

    def draw_particles(self,
                       surface:pygame.Surface,
                       camera_position:pygame.Vector2):
        for p in self.particles:
            p.draw(surface, camera_position)

    def draw(self,
             surface:pygame.Surface,
             screen_bounds:pygame.Rect,
             camera_position:pygame.Vector2):
        self.draw_chunks(surface, screen_bounds, camera_position)
        self.draw_entities(surface, camera_position)
        self.draw_particles(surface, camera_position)