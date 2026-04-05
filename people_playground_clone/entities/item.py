from __future__ import annotations

import math
import pygame
import pymunk
from config import MATERIALS, COLORS, COLLISION_TYPES


class Item:
    def __init__(self, world, name: str, pos: tuple[float, float], size: tuple[float, float], material: str = "wood", color: tuple[int, int, int] | None = None, dynamic: bool = True) -> None:
        self.world = world
        self.name = name
        self.material = material
        self.size = size
        self.color = color or COLORS.get(material, (180, 180, 180))
        self.max_hp = MATERIALS[material]["hp"]
        self.hp = self.max_hp
        self.break_impulse = MATERIALS[material]["break_impulse"]
        self.on_fire = False
        self.fire_t = 0.0
        self.frozen = False
        self.serializable = True

        w, h = size
        density = MATERIALS[material]["density"]
        if dynamic:
            self.mass = max(0.2, w * h / 1200 * density)
            moment = pymunk.moment_for_box(self.mass, size)
            self.body = pymunk.Body(self.mass, moment)
        else:
            self.mass = 0.0
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos

        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = MATERIALS[material]["friction"]
        self.shape.elasticity = MATERIALS[material]["elasticity"]
        self.shape.collision_type = COLLISION_TYPES["default"]
        self.shape.entity_ref = self

        self.world.add(self.body, self.shape)

    def apply_damage(self, damage: float, at: tuple[float, float] | None = None) -> None:
        self.hp -= damage
        if at:
            self.world.engine.particles.emit(at, 6, (150, 22, 22), speed=95, spread=90, size=2.0, lifetime=0.6)
        if self.hp <= 0:
            self.destroy()

    def ignite(self) -> None:
        if MATERIALS[self.material]["flammable"] <= 0:
            return
        self.on_fire = True
        self.fire_t = 4.0 * MATERIALS[self.material]["flammable"]

    def update(self, dt: float) -> None:
        if self.frozen:
            self.body.velocity = (0, 0)
            self.body.angular_velocity = 0

        if self.on_fire:
            self.fire_t -= dt
            self.apply_damage(4 * dt)
            self.world.engine.particles.emit(self.body.position, 1, (255, 122, 28), speed=40, spread=30, size=2.2, lifetime=0.4, gravity=-20)
            if self.fire_t <= 0:
                self.on_fire = False

    def draw(self, surf: pygame.Surface, camera, size: tuple[int, int]) -> None:
        points = [camera.world_to_screen(self.body.local_to_world(v), size) for v in self.shape.get_vertices()]
        int_pts = [(int(p.x), int(p.y)) for p in points]
        pygame.draw.polygon(surf, self.color, int_pts)
        pygame.draw.polygon(surf, (30, 30, 35), int_pts, 2)

        if self.on_fire:
            c = camera.world_to_screen(self.body.position, size)
            pygame.draw.circle(surf, (255, 130, 45), (int(c.x), int(c.y)), max(2, int(10 * camera.zoom)), 1)

    def rotate(self, angle_deg: float) -> None:
        self.body.angle += math.radians(angle_deg)

    def toggle_freeze(self) -> None:
        self.frozen = not self.frozen
        self.body.body_type = pymunk.Body.KINEMATIC if self.frozen else pymunk.Body.DYNAMIC

    def toggle_gravity(self) -> None:
        self.body.velocity_func = (lambda body, gravity, damping, dt: pymunk.Body.update_velocity(body, (0, 0), damping, dt)) if self.body.velocity_func is None else None

    def destroy(self) -> None:
        self.world.engine.to_remove.append(self)

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "material": self.material,
            "size": [self.size[0], self.size[1]],
            "pos": [self.body.position.x, self.body.position.y],
            "angle": self.body.angle,
            "hp": self.hp,
            "on_fire": self.on_fire,
        }
