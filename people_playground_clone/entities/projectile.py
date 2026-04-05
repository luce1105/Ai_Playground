from __future__ import annotations

import pygame
import pymunk
from config import COLLISION_TYPES


class Projectile:
    def __init__(self, world, pos: tuple[float, float], velocity: tuple[float, float], damage: float = 22, ttl: float = 3.2):
        self.world = world
        self.name = "Projectile"
        self.damage = damage
        self.ttl = ttl
        self.serializable = False

        self.body = pymunk.Body(0.12, pymunk.moment_for_circle(0.12, 0, 3))
        self.body.position = pos
        self.body.velocity = velocity
        self.shape = pymunk.Circle(self.body, 3)
        self.shape.sensor = False
        self.shape.collision_type = COLLISION_TYPES["projectile"]
        self.shape.entity_ref = self
        self.shape.friction = 0.1
        self.shape.elasticity = 0.1
        world.add(self.body, self.shape)

    def update(self, dt: float) -> None:
        self.ttl -= dt
        if self.ttl <= 0:
            self.destroy()

    def draw(self, surf: pygame.Surface, camera, size: tuple[int, int]) -> None:
        p = camera.world_to_screen(self.body.position, size)
        pygame.draw.circle(surf, (244, 218, 140), (int(p.x), int(p.y)), max(1, int(3 * camera.zoom)))

    def destroy(self) -> None:
        self.world.engine.to_remove.append(self)
