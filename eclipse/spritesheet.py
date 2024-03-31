import pygame

class Spritesheet(object):
    def __init__(self,
                 image_path:str,
                 color_key:tuple=(0,0,0)):
        self.color_key = color_key
        self.surface = pygame.image.load(image_path)
        self.surface.set_colorkey(self.color_key)
    
    def get(self,
            rect:pygame.Rect) -> pygame.Surface:
        """Gets a sprite from the sheet, given a bounding rect.

        Args:
            rect (pygame.Rect): The sprite rect.

        Returns:
            pygame.Surface: The sprite surface.
        """
        sprite_surface = pygame.Surface(rect.size)
        sprite_surface.fill(self.color_key)
        sprite_surface.set_colorkey(self.color_key)
        sprite_surface.blit(self.surface, (-rect.x, -rect.y))
        return sprite_surface