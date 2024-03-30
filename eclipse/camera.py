import pygame

class Camera(object):
    """The Camera class allows for smooth interpolation
    between a target and current position, based on some
    snap amount.
    """
    position: pygame.Vector2
    target: pygame.Vector2
    snap: float

    def __init__(self):
        self.position = pygame.Vector2()
        self.target = pygame.Vector2()
        self.snap = 7.0
    
    def update(self, dt:float):
        """Updates the camera position to bring it closer to
        the target position, based on the snap amount.

        Args:
            dt (float): Time delta since the last update.
        """
        self.position += (self.target-self.position)*self.snap*dt