import typing as t
import pygame

from .tile import Tile, TileRegistry

class Chunk():
    """Chunks represent a square region of tiles in an Eclipse World instance.

    One Chunk is 16x16 tiles.

    Chunks store their own cached surface image, which is updated through
    the chunk.update_cached_surface() method, which is called after running
    chunk.set_tile()
    """
    tiles: t.Dict[str, Tile]
    surface: pygame.Surface
    tile_registry: TileRegistry

    def __init__(self, tile_registry:TileRegistry):
        self.tiles = {}
        self.reset_cached_surface()
        self.tile_registry = tile_registry
    
    def reset_cached_surface(self):
        self.surface = pygame.Surface((16*16, 16*16))
        self.surface.fill((0,0,0))
        self.surface.set_colorkey((0,0,0))
    
    def update_cached_surface(self):
        """Updates the chunk's cached surface.
        """
        self.surface.fill((0,0,0))
        for y in range(16):
            for x in range(16):
                tile = self.get_tile(x, y)
                if tile is None: continue
                pixel_x = x*16
                pixel_y = y*16
                tile_registry_entry = self.tile_registry.get_tile_registry_entry(tile.identifier)
                self.surface.blit(tile_registry_entry.surface, (pixel_x, pixel_y))
    
    def get_tile_key(self, x:int, y:int) -> str:
        """Convert an x, y coordinate into a string
        key used in the hashmap for tile access.

        Args:
            x (int): X coordinate of the tile in the chunk.
            y (int): Y coordinate of the tile in the chunk.

        Returns:
            str: The hashmap key for this tile.
        """
        return f"c{x},{y}"

    def get_tile(self, x:int, y:int) -> t.Union[Tile, None]:
        key = self.get_tile_key(x, y)
        return self.tiles.get(key)
    
    def set_tile(self, x:int, y:int, tile:Tile):
        self.tiles[self.get_tile_key(x, y)] = tile
        self.update_cached_surface()
    
    def chunk_location_to_tile_location(self, x:float, y:float):
        return (int(x//16), int(y//16))
    
    def collide_point(self, point:pygame.Vector2) -> bool:
        """Checks if a given point (in chunk space) collides
        with any tiles.

        Args:
            point (pygame.Vector2): The point in chunk space.

        Returns:
            bool: Whether the point collided.
        """
        tile_x, tile_y = self.chunk_location_to_tile_location(point.x, point.y)
        tile = self.get_tile(tile_x, tile_y)
        if tile is None:
            return False
        tile_registry_entry = self.tile_registry.get_tile_registry_entry(tile.identifier)
        # Convert the point to tile-space and check
        # whether it collides in the tile
        point_tilespace = pygame.Vector2(
            point.x%16,
            point.y%16)
        return tile_registry_entry.collide_point(point_tilespace)
