import typing as t

import pygame

class TileRegistryEntry(object):
    identifier:str
    def __init__(self, identifier:str, surface:pygame.Surface):
        self.identifier = identifier
        self.surface = surface
        self.surface.set_colorkey((0,0,0))

        # Collision information should also be stored in the TileRegistryEntry;
        self.rects = [pygame.Rect((0,0), (16,16))]

    def collide_point(self, point:pygame.Vector2):
        for rect in self.rects:
            if rect.collidepoint(point):
                return True
        return False
    
    def collide_rect(self, rect:pygame.Rect, offset:pygame.Vector2):
        offset_rect = pygame.Rect(rect.left-offset.x, rect.top-offset.y, rect.width, rect.height)
        for rect in self.rects:
            if rect.colliderect(offset_rect):
                return True
        return False

class TileRegistry(object):
    registry: t.Dict[str, TileRegistryEntry]
    def __init__(self):
        self.registry = {}
    
    def register_tile(self, tile_registry_entry:TileRegistryEntry) -> TileRegistryEntry:
        """Adds a tile to the tile registry.

        Args:
            tile_registry_entry (TileRegistryEntry): Tile to register.
        """
        self.registry[tile_registry_entry.identifier] = tile_registry_entry
        return tile_registry_entry
    
    def get_tile_registry_entry(self, identifier:str)\
            -> t.Union[TileRegistryEntry, None]:
        return self.registry.get(identifier)
    
class Tile(object):
    identifier: str
    def __init__(self, identifier:str):
        self.identifier = identifier