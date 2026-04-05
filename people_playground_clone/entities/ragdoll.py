from __future__ import annotations

import pygame
import pymunk
from config import MATERIALS, COLLISION_TYPES


class RagdollLimb:
    def __init__(self, world, mass: float, moment: float, pos: tuple[float, float], radius: float, color: tuple[int, int, int]):
        self.world = world
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = MATERIALS["flesh"]["friction"]
        self.shape.elasticity = MATERIALS["flesh"]["elasticity"]
        self.shape.collision_type = COLLISION_TYPES["character"]
        self.shape.entity_ref = None
        self.radius = radius
        self.color = color
        self.world.add(self.body, self.shape)

    def draw(self, surf: pygame.Surface, camera, size: tuple[int, int]) -> None:
        p = camera.world_to_screen(self.body.position, size)
        pygame.draw.circle(surf, self.color, (int(p.x), int(p.y)), max(2, int(self.radius * camera.zoom)))
