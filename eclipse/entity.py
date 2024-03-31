from turtle import pos
import typing as t
import pygame

if t.TYPE_CHECKING:
    from .world import World

# Entity physics attributes default values
gravity_default = pygame.Vector2(0, 300)
drag_default = 0.2
restitution_default=0.0
slipperiness_default=0.5

class Entity(object):
    world:"World"
    collider_rect: pygame.Rect
    velocity: pygame.Vector2
    gravity:pygame.Vector2
    drag:float
    restitution:float
    slipperiness:float

    def __init__(self,
                 world:"World",
                 position:pygame.Vector2,
                 collider_size:t.Tuple[int, int],
                 gravity:pygame.Vector2=gravity_default,
                 drag=drag_default,
                 restitution=restitution_default,
                 slipperiness=slipperiness_default):
        # Important reference properties
        self.world = world

        # Collider rect
        self.collider_rect = pygame.Rect(
            position.x-collider_size[0]//2,
            position.y-collider_size[1],
            collider_size[0],
            collider_size[1])
        
        self.velocity = pygame.Vector2(0,0)
        self.position = self.get_rect_position()
        
        # Physics properties
        self.gravity = gravity
        self.drag = drag
        self.restitution = restitution
        self.slipperiness = slipperiness
    
    def update_rect_position(self):
        self.collider_rect.centerx = self.position.x
        self.collider_rect.bottom = self.position.y

    def get_rect_position(self) -> pygame.Vector2:
        return pygame.Vector2(
            self.collider_rect.centerx,
            self.collider_rect.bottom)
    
    def apply_impulse(self, impulse:pygame.Vector2):
        self.velocity += impulse
    
    def update(self, dt:float):
        self.position.x += self.velocity.x*dt
        self.update_rect_position()
        if self.world.collide_rect(self.collider_rect):
            self.position.x -= self.velocity.x*dt
            self.velocity.x *= -self.restitution
            self.velocity.y *= self.slipperiness
        
        self.position.y += self.velocity.y*dt
        self.update_rect_position()
        if self.world.collide_rect(self.collider_rect):
            self.position.y -= self.velocity.y*dt
            self.velocity.y *= -self.restitution
            self.velocity.x *= self.slipperiness
        
        self.update_rect_position()

        self.velocity += self.gravity*dt
        self.velocity -= self.velocity*self.drag*dt

    def draw(self,
             surface:pygame.Surface,
             camera_position:pygame.Vector2) -> None:
        pygame.draw.rect(
            surface=surface,
            color=(255, 255, 255),
            rect=pygame.Rect(
                self.collider_rect.left-camera_position.x,
                self.collider_rect.top-camera_position.y,
                self.collider_rect.width,
                self.collider_rect.height
            ),
            width=2
        )