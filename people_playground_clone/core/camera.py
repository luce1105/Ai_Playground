from __future__ import annotations

from dataclasses import dataclass
import pygame


@dataclass
class Camera:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    zoom_target: float = 1.0
    min_zoom: float = 0.25
    max_zoom: float = 2.7
    move_speed: float = 900.0
    smoothing: float = 8.0

    def update(self, dt: float, keys, settings: dict) -> None:
        speed = self.move_speed * dt * settings.get("camera_sensitivity", 1.0)
        if keys[pygame.K_a]:
            self.x -= speed / self.zoom
        if keys[pygame.K_d]:
            self.x += speed / self.zoom
        if keys[pygame.K_w]:
            self.y -= speed / self.zoom
        if keys[pygame.K_s]:
            self.y += speed / self.zoom

        self.zoom += (self.zoom_target - self.zoom) * min(1.0, dt * self.smoothing)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

    def add_zoom(self, amount: float) -> None:
        self.zoom_target = max(self.min_zoom, min(self.max_zoom, self.zoom_target + amount))

    def world_to_screen(self, world_pos: pygame.Vector2 | tuple, screen_size: tuple[int, int]) -> pygame.Vector2:
        w = pygame.Vector2(world_pos)
        return pygame.Vector2((w.x - self.x) * self.zoom + screen_size[0] / 2, (w.y - self.y) * self.zoom + screen_size[1] / 2)

    def screen_to_world(self, screen_pos: tuple[int, int], screen_size: tuple[int, int]) -> pygame.Vector2:
        s = pygame.Vector2(screen_pos)
        return pygame.Vector2((s.x - screen_size[0] / 2) / self.zoom + self.x, (s.y - screen_size[1] / 2) / self.zoom + self.y)
