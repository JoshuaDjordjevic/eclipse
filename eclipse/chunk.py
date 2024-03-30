import typing as t
import pygame

from .tile import Tile

class Chunk():
    """Chunks represent a square region of tiles in an Eclipse World instance.

    One Chunk is 16x16 tiles.

    Chunks store their own cached surface image, which is updated through
    the chunk.update_cached_surface() method, which is called after running
    chunk.set_tile()
    """
    tiles: t.Dict[str, Tile]
    surface: pygame.Surface

    def __init__(self):
        self.tiles = {}
        self.reset_cached_surface()
    
    def reset_cached_surface(self):
        self.surface = pygame.Surface((16*16, 16*16))
        self.surface.fill((0,0,0))
        self.surface.set_colorkey((0,0,0))
    
    def update_cached_surface(self):
        """Updates the chunk's cached surface.
        """
        self.surface.fill((0,0,0))
        # TODO: draw tiles
    
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