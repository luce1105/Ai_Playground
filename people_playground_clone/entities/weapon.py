from __future__ import annotations

import pygame
from entities.item import Item
from entities.projectile import Projectile


class Weapon(Item):
    def __init__(self, world, name: str, pos: tuple[float, float], weapon_type: str = "pistol") -> None:
        super().__init__(world, name, pos, (46, 14), "metal", (78, 86, 101), dynamic=True)
        self.weapon_type = weapon_type
        self.cooldown = 0.0
        self.stats = {
            "pistol": {"rate": 0.25, "speed": 920, "damage": 20},
            "rifle": {"rate": 0.09, "speed": 1080, "damage": 17},
            "shotgun": {"rate": 0.65, "speed": 840, "damage": 10},
        }

    def update(self, dt: float) -> None:
        super().update(dt)
        self.cooldown = max(0.0, self.cooldown - dt)

    def shoot_at(self, target_pos: tuple[float, float]) -> None:
        if self.weapon_type not in self.stats:
            return
        if self.cooldown > 0:
            return
        stat = self.stats[self.weapon_type]
        self.cooldown = stat["rate"]
        src = pygame.Vector2(self.body.position)
        direction = pygame.Vector2(target_pos) - src
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()

        pellets = 6 if self.weapon_type == "shotgun" else 1
        for i in range(pellets):
            spread = pygame.Vector2(0, 0)
            if pellets > 1:
                spread = pygame.Vector2(1, 0).rotate((i - pellets // 2) * 6)
            vel = tuple((direction + spread * 0.05).normalize() * stat["speed"])
            proj = Projectile(self.world, tuple(src + direction * 28), vel, damage=stat["damage"])
            self.world.engine.projectiles.append(proj)

        self.body.apply_impulse_at_local_point((-180, 0), (0, 0))
        self.world.engine.audio.play("gunshot")
