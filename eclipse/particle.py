import typing as t
import pygame

if t.TYPE_CHECKING:
    from .world import World

type_colour = t.Tuple[int, int, int]
gravity_default = pygame.Vector2(0, 150)

class Particle(object):
    world:"World"
    position:pygame.Vector2
    velocity:pygame.Vector2 
    lifetime:float
    lifetime_max:float
    colour:type_colour
    radius:int
    gravity:pygame.Vector2
    drag:float
    resistution:float
    slipperiness:float
    expire_on_collision:bool

    def __init__(self,
                 world:"World",
                 position:pygame.Vector2,
                 velocity:pygame.Vector2,
                 lifetime:float,
                 colour:type_colour,
                 radius:int,
                 gravity:pygame.Vector2=gravity_default,
                 drag:float=0.2,
                 restitution:float=0.5,
                 slipperiness:float=0.95,
                 expire_on_collision:bool=False):
        # Important reference properties
        self.world = world

        # Position properties
        self.position = position
        self.velocity = velocity

        # Lifetime properties
        self.lifetime = lifetime
        self.lifetime_max = lifetime

        # Visual properties
        self.colour = colour
        self.radius = radius

        # Physics properties
        self.gravity = gravity
        self.drag = drag
        self.restitution = restitution
        self.slipperiness = slipperiness

        self.expire_on_collision = expire_on_collision
    
    def update(self, dt:float):
        # Decrease lifetime by delta, and if the time
        # is up it means the particle should die
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        
        # Update position and bounce off collisions
        self.position.x += self.velocity.x*dt
        if self.world.collide_point(self.position):
            self.position.x -= self.velocity.x*dt
            self.velocity.x *= -self.restitution
            self.velocity.y *= self.slipperiness
            if self.expire_on_collision:
                return False
        
        self.position.y += self.velocity.y*dt
        if self.world.collide_point(self.position):
            self.position.y -= self.velocity.y*dt
            self.velocity.y *= -self.restitution
            self.velocity.x *= self.slipperiness
            if self.expire_on_collision:
                return False
        
        # Update velocity
        self.velocity += self.gravity*dt

        # Apply drag
        self.velocity -= self.velocity*self.drag*dt
        
        # Return the life state, which should be True
        return True

    def draw(self,
             surface:pygame.Surface,
             camera_position:pygame.Vector2) -> None:
        pygame.draw.circle(
            surface=surface,
            color=self.colour,
            center=self.position-camera_position,
            radius=self.radius)