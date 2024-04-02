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
    slipperiness_x:float=-1.0
    slipperiness_y:float=1.0

    time_since_grounded:float
    time_since_last_jump:float

    is_grounded:bool=False
    is_moving:bool=False
    is_falling:bool=False

    def __init__(self,
                 world:"World",
                 position:pygame.Vector2,
                 collider_size:pygame.Vector2,
                 gravity:pygame.Vector2=gravity_default,
                 drag=drag_default,
                 restitution=restitution_default,
                 slipperiness=slipperiness_default):
        # Important reference properties
        self.world = world

        # Collider rect
        self.collider_rect = pygame.Rect(
            position.x-collider_size.x//2,
            position.y-collider_size.y,
            collider_size.x,
            collider_size.y)
        
        self.velocity = pygame.Vector2(0,0)
        self.position = self.get_rect_position()
        
        # Physics properties
        self.gravity = gravity
        self.drag = drag
        self.restitution = restitution
        self.slipperiness = slipperiness

        self.time_since_grounded = 0.0
        self.time_since_last_jump = 0.0
    
    def update_rect_position(self):
        self.collider_rect.centerx = self.position.x
        self.collider_rect.bottom = self.position.y

    def get_rect_position(self) -> pygame.Vector2:
        return pygame.Vector2(
            self.collider_rect.centerx,
            self.collider_rect.bottom)
    
    def apply_impulse(self, impulse:pygame.Vector2):
        self.velocity += impulse
    
    def jump(self, force:float=200.0):
        if self.is_grounded and self.time_since_last_jump>0.1:
            self.time_since_last_jump = 0.0
            self.is_grounded = False
            self.apply_impulse(pygame.Vector2(0, -force))
    
    def move_horizontal(self,
                        target_velocity:float,
                        acceleration:float,
                        dt:float):
        """Applies some horizontal impulse to the entity
        in order to push it to reach a target velocity,
        provided some acceleration factor and delta-time.

        This function should be called in custom update functions.

        Args:
            target_velocity (float): The velocity to reach.
            acceleration (float): The acceleration amount.
            dt (float): Delta time.
        """
        difference = target_velocity-self.velocity.x
        if target_velocity < 0:
            difference = min(0, difference)
        elif target_velocity > 0:
            difference = max(0, difference)
        impulse_x = difference*acceleration*dt
        self.velocity.x += impulse_x

    def on_collision(self, axis:int):
        ...
    
    def update(self, dt:float):
        self.is_grounded = False

        self.position.x += self.velocity.x*dt
        self.update_rect_position()
        if self.world.collide_rect(self.collider_rect):
            self.on_collision(axis=0)
            self.position.x -= self.velocity.x*dt
            self.velocity.x *= -self.restitution
            self.velocity.y *= self.slipperiness if self.slipperiness_y == -1 else self.slipperiness_y
        
        self.position.y += self.velocity.y*dt
        self.update_rect_position()
        if self.world.collide_rect(self.collider_rect):
            self.on_collision(axis=1)
            if self.velocity.y > 0:
                self.time_since_grounded = 0.0
            self.position.y -= self.velocity.y*dt
            self.velocity.y *= -self.restitution
            self.velocity.x *= self.slipperiness if self.slipperiness_x == -1 else self.slipperiness_x

        self.update_rect_position()

        self.velocity += self.gravity*dt
        self.velocity -= self.velocity*self.drag*dt

        self.time_since_grounded += dt
        self.time_since_last_jump += dt

        self.is_grounded = self.time_since_grounded < 0.1
        self.is_moving = abs(self.velocity.x)>0.01
        self.is_falling = self.velocity.y>0 and not self.is_grounded

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