from __future__ import annotations

import random
import pygame
import pymunk
from entities.ragdoll import RagdollLimb


class Human:
    def __init__(self, world, pos: tuple[float, float]) -> None:
        self.world = world
        self.name = "Human"
        self.material = "flesh"
        self.max_hp = 130.0
        self.hp = self.max_hp
        self.frozen = False
        self.on_fire = False
        self.serializable = True
        self.mass = 12.0
        outfit = random.choice([(68, 151, 211), (122, 171, 91), (173, 112, 186), (205, 140, 98)])

        x, y = pos
        self.head = RagdollLimb(world, 2.2, 15, (x, y - 35), 12, (225, 184, 158))
        self.torso = RagdollLimb(world, 4.8, 28, (x, y), 16, outfit)
        self.left_arm = RagdollLimb(world, 1.6, 10, (x - 20, y - 4), 8, outfit)
        self.right_arm = RagdollLimb(world, 1.6, 10, (x + 20, y - 4), 8, outfit)
        self.left_leg = RagdollLimb(world, 2.0, 12, (x - 10, y + 32), 9, (55, 58, 64))
        self.right_leg = RagdollLimb(world, 2.0, 12, (x + 10, y + 32), 9, (55, 58, 64))
        self.limbs = [self.head, self.torso, self.left_arm, self.right_arm, self.left_leg, self.right_leg]
        for limb in self.limbs:
            limb.shape.entity_ref = self

        self.joints = [
            pymunk.PinJoint(self.head.body, self.torso.body, (0, 9), (0, -14)),
            pymunk.DampedSpring(self.head.body, self.torso.body, (0, 9), (0, -14), 2, 420, 18),
            pymunk.PinJoint(self.left_arm.body, self.torso.body, (4, 0), (-14, -4)),
            pymunk.PinJoint(self.right_arm.body, self.torso.body, (-4, 0), (14, -4)),
            pymunk.PinJoint(self.left_leg.body, self.torso.body, (0, -2), (-7, 15)),
            pymunk.PinJoint(self.right_leg.body, self.torso.body, (0, -2), (7, 15)),
        ]
        self.world.add(*self.joints)

    @property
    def body(self):
        return self.torso.body

    def apply_damage(self, damage: float, at: tuple[float, float] | None = None) -> None:
        self.hp -= damage
        if self.world.engine.settings.get("show_blood", True):
            point = at or self.torso.body.position
            self.world.engine.particles.emit(point, 8, (137, 26, 31), speed=170, spread=130, size=2.7, lifetime=0.9)
            self.world.engine.particles.add_decal(point, (111, 24, 26), radius=3.5)
        if self.hp <= 0:
            self.hp = 0

    def update(self, dt: float) -> None:
        if self.frozen:
            for limb in self.limbs:
                limb.body.velocity = (0, 0)
                limb.body.angular_velocity = 0
        if self.on_fire:
            self.apply_damage(7 * dt)
            self.world.engine.particles.emit(self.torso.body.position, 1, (255, 140, 35), speed=70, spread=40, size=2.5, lifetime=0.5)

    def draw(self, surf: pygame.Surface, camera, size: tuple[int, int]) -> None:
        pairs = [
            (self.head.body.position, self.torso.body.position),
            (self.left_arm.body.position, self.torso.body.position),
            (self.right_arm.body.position, self.torso.body.position),
            (self.left_leg.body.position, self.torso.body.position),
            (self.right_leg.body.position, self.torso.body.position),
        ]
        for a, b in pairs:
            sa = camera.world_to_screen(a, size)
            sb = camera.world_to_screen(b, size)
            pygame.draw.line(surf, (53, 56, 66), (int(sa.x), int(sa.y)), (int(sb.x), int(sb.y)), max(1, int(6 * camera.zoom)))
        for limb in self.limbs:
            limb.draw(surf, camera, size)

    def rotate(self, angle_deg: float) -> None:
        for limb in self.limbs:
            limb.body.angle += angle_deg * 0.017

    def toggle_freeze(self) -> None:
        self.frozen = not self.frozen
        for limb in self.limbs:
            limb.body.body_type = pymunk.Body.KINEMATIC if self.frozen else pymunk.Body.DYNAMIC

    def toggle_gravity(self) -> None:
        for limb in self.limbs:
            limb.body.velocity_func = (lambda body, gravity, damping, dt: pymunk.Body.update_velocity(body, (0, 0), damping, dt)) if limb.body.velocity_func is None else None

    def ignite(self) -> None:
        self.on_fire = True

    def destroy(self) -> None:
        self.world.engine.to_remove.append(self)

    def to_dict(self) -> dict:
        return {
            "type": "Human",
            "pos": [self.torso.body.position.x, self.torso.body.position.y],
            "hp": self.hp,
        }
