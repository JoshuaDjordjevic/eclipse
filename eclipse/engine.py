import typing as t

import pygame

from . import World
from . import Camera
from .tile import TileRegistry

class Engine(object):
    worlds: t.Dict[str, World]
    camera: Camera
    tile_registry: TileRegistry

    def __init__(self):
        self.worlds = {}
        self.camera = Camera()
        self.tile_registry = TileRegistry()
    
    def create_new_world(self, name:str) -> World:
        w = World(self.tile_registry)
        self.worlds[name] = w
        return w

    def screen_space_to_world_space(self,
                                    point:pygame.Vector2,
                                    display_scale:float=1.0) -> pygame.Vector2:
        return pygame.Vector2(
            point.x/display_scale+self.camera.position.x,
            point.y/display_scale+self.camera.position.y)

    def world_space_to_screen_space(self,
                                    point:pygame.Vector2,
                                    display_scale:float=1.0) -> pygame.Vector2:
        return pygame.Vector2(
            (point.x-self.camera.position.x)*display_scale,
            (point.y-self.camera.position.y)*display_scale)
    
    def world_space_rect_to_screen_space_rect(self,
                                              rect:pygame.Rect,
                                              display_scale:float=1.0) -> pygame.Rect:
        return pygame.Rect(
            (rect.left-self.camera.position.x)*display_scale,
            (rect.top-self.camera.position.y)*display_scale,
            rect.width*display_scale,
            rect.height*display_scale)