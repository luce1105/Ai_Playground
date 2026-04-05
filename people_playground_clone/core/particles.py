from __future__ import annotations

from dataclasses import dataclass
import random
import pygame


@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    color: tuple[int, int, int]
    size: float
    lifetime: float
    max_lifetime: float
    gravity: float = 0.0


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self.decals: list[tuple[pygame.Vector2, tuple[int, int, int], float]] = []
        self.max_particles = 4000
        self.max_decals = 1000

    def emit(self, pos: tuple[float, float], count: int, color: tuple[int, int, int], spread: float = 120.0, speed: float = 160.0, size: float = 3.0, lifetime: float = 1.0, gravity: float = 400.0) -> None:
        count = min(count, self.max_particles - len(self.particles))
        base = pygame.Vector2(pos)
        for _ in range(max(0, count)):
            v = pygame.Vector2(random.uniform(-spread, spread), random.uniform(-spread, spread))
            if v.length_squared() > 0:
                v.scale_to_length(random.uniform(0.2, 1.0) * speed)
            self.particles.append(Particle(base.copy(), v, color, random.uniform(0.6, 1.35) * size, lifetime, lifetime, gravity))

    def add_decal(self, pos: tuple[float, float], color: tuple[int, int, int], radius: float = 5.0) -> None:
        if len(self.decals) >= self.max_decals:
            self.decals.pop(0)
        self.decals.append((pygame.Vector2(pos), color, radius))

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self.particles:
            p.lifetime -= dt
            if p.lifetime <= 0:
                continue
            p.vel.y += p.gravity * dt
            p.pos += p.vel * dt
            alive.append(p)
        self.particles = alive

    def draw(self, surf: pygame.Surface, camera, screen_size: tuple[int, int]) -> None:
        for pos, color, radius in self.decals:
            s = camera.world_to_screen(pos, screen_size)
            pygame.draw.circle(surf, color, (int(s.x), int(s.y)), max(1, int(radius * camera.zoom)))

        for p in self.particles:
            alpha = max(0, min(255, int(255 * (p.lifetime / p.max_lifetime))))
            s = camera.world_to_screen(p.pos, screen_size)
            sz = max(1, int(p.size * camera.zoom))
            c = pygame.Color(*p.color)
            c.a = alpha
            p_surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, c, (sz, sz), sz)
            surf.blit(p_surf, (int(s.x - sz), int(s.y - sz)))
