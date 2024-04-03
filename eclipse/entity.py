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

    lifetime:float
    timer_at_grounded:float
    timer_at_last_jump:float

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

        self.lifetime = 0.0
        self.timer_at_grounded = 0.0
        self.timer_at_last_jump = 0.0
    
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
        if not self.is_grounded:
            return False
        if self.lifetime-self.timer_at_last_jump < 0.1:
            return False
        self.timer_at_last_jump = self.lifetime
        self.is_grounded = False
        self.apply_impulse(pygame.Vector2(0, -force))
        return True
    
    def accelerate_to_velocity(self,
                               x:float=...,
                               y:float=...,
                               acceleration:float=1.0,
                               dt:float=0.0,
                               allow_deceleration:bool=False) -> None:
        """Accelerates the entity to reach some provided
        target velocity, using smooth % acceleration.
        This means that as t->infinity, a->infinity.

        If x or y are not specified, acceleration will not
        be applied in that axis.

        Args:
            x (float, optional): X target velocity. Defaults to ....
            y (float, optional): Y target velocity. Defaults to ....
            acceleration (float, optional): Acceleration factor. Defaults to 1.0.
            dt (float, optional): Deltatime. Defaults to 0.0.
            allow_deceleration (bool, optional): Whether to allow
            decelerating to reach the target velocity.
            Defaults to False.
        """
        if x != ...:
            difference = x-self.velocity.x
            if not allow_deceleration:
                if x < 0:
                    difference = min(0, difference)
                elif x > 0:
                    difference = max(0, difference)
            # TODO: Separate dt from impulse to allow
            # capping the acceleration force, to prevent a->infinity
            impulse_x = difference*acceleration*dt
            self.velocity.x += impulse_x
        if y != ...:
            difference = y-self.velocity.y
            if not allow_deceleration:
                if y < 0:
                    difference = min(0, difference)
                elif y > 0:
                    difference = max(0, difference)
            impulse_y = difference*acceleration*dt
            self.velocity.y += impulse_y
    
    def move_horizontal(self,
                        target_velocity:float,
                        acceleration:float,
                        dt:float):
        """Superceeded by accelerate_to_velocity"""
        self.accelerate_to_velocity(
            x=target_velocity,
            acceleration=acceleration,
            dt=dt)

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
                self.timer_at_grounded = self.lifetime
            self.position.y -= self.velocity.y*dt
            self.velocity.y *= -self.restitution
            self.velocity.x *= self.slipperiness if self.slipperiness_x == -1 else self.slipperiness_x

        self.update_rect_position()

        self.velocity += self.gravity*dt
        self.velocity -= self.velocity*self.drag*dt

        self.lifetime += dt

        self.is_grounded = self.lifetime-self.timer_at_grounded < 0.1
        self.is_moving = abs(self.velocity.x)>0.01
        self.is_falling = self.velocity.y>0 and not self.is_grounded

    def update_movement(self,
                         move_left:bool,
                         move_right:bool,
                         jump:bool,
                         acceleration:float,
                         acceleration_air:float,
                         movement_speed:float,
                         jump_force:float,
                         dt:float):
        """Allows this entity to move with basic
        controls provided with speed and force configurations.

        WARNING: This function has a slight quirk. It will
        set slipperiness_x to slipperiness when no left or right
        movement is applied. Please take note of this if you run
        into weird issues and need to debug.

        Args:
            move_left (bool): ...
            move_right (bool): ...
            jump (bool): ...
            acceleration (float): Accleration speed.
            acceleration_air (float): Accleration speed in air.
            movement_speed (float): Movement speed.
            jump_force (float): Force to jump with.
            dt (float): Deltatime.
        """
        self.slipperiness_x = self.slipperiness
        move_x = 0
        if move_left:
            move_x = -movement_speed
        elif move_right:
            move_x = movement_speed
        if move_left and move_right:
            move_x = 0
        if move_x != 0:
            self.slipperiness_x = 1
            self.accelerate_to_velocity(
                x=move_x,
                acceleration=acceleration if self.is_grounded else acceleration_air,
                dt=dt,)
        if jump:
            self.jump(jump_force)

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