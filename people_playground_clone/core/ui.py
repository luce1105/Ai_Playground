from __future__ import annotations

from dataclasses import dataclass
import pygame
from config import COLORS


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    callback: callable
    hover_t: float = 0.0


class UIManager:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont("Segoe UI", 22)
        self.small = pygame.font.SysFont("Segoe UI", 16)
        self.buttons: list[Button] = []
        self.menu_open = True
        self.spawn_open = True
        self.spawn_category = "Humans"
        self.categories = ["Humans", "Weapons", "Tools", "Materials", "Decor", "Mechanisms", "Effects", "Other"]
        self.spawn_items = {
            "Humans": ["Human"],
            "Weapons": ["Pistol", "Rifle", "Shotgun", "Knife", "Hammer", "Crowbar"],
            "Tools": ["Rope", "Freeze Tool", "Delete Tool", "Injector", "Shock Tool"],
            "Materials": ["Wood Crate", "Metal Block", "Glass Panel", "Stone Brick", "Rubber Wheel", "Explosive Barrel"],
            "Decor": ["Lamp", "Door", "Platform"],
            "Mechanisms": ["Button", "Spike"],
            "Effects": ["Fire Emitter", "Smoke Emitter"],
            "Other": ["Barrel", "Brick"],
        }

    def build_main_menu(self, size: tuple[int, int], callbacks: dict) -> None:
        w, h = size
        bw, bh = 320, 56
        start_y = h // 2 - 170
        labels = ["Играть", "Настройки", "Песочница", "Загрузить сохранение", "Выход"]
        keys = ["play", "settings", "sandbox", "load", "quit"]
        self.buttons = []
        for i, label in enumerate(labels):
            rect = pygame.Rect(w // 2 - bw // 2, start_y + i * 72, bw, bh)
            self.buttons.append(Button(rect, label, callbacks[keys[i]]))

    def draw_main_menu(self, dt: float, mouse_pos: tuple[int, int]) -> None:
        self.screen.fill((13, 16, 21))
        w, h = self.screen.get_size()
        for y in range(0, h, 3):
            c = 22 + int(16 * (y / h))
            pygame.draw.line(self.screen, (c, c + 8, c + 20), (0, y), (w, y))

        title = pygame.font.SysFont("Segoe UI Semibold", 64).render("People Playground Clone", True, COLORS["text"])
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 90))

        for b in self.buttons:
            is_hover = b.rect.collidepoint(mouse_pos)
            b.hover_t = min(1.0, b.hover_t + dt * 8) if is_hover else max(0.0, b.hover_t - dt * 8)
            c = pygame.Color(*COLORS["panel"])
            c.r = int(c.r + (COLORS["accent"][0] - c.r) * b.hover_t * 0.35)
            c.g = int(c.g + (COLORS["accent"][1] - c.g) * b.hover_t * 0.35)
            c.b = int(c.b + (COLORS["accent"][2] - c.b) * b.hover_t * 0.35)
            pygame.draw.rect(self.screen, c, b.rect, border_radius=12)
            pygame.draw.rect(self.screen, COLORS["outline"], b.rect, 2, border_radius=12)
            text = self.font.render(b.text, True, COLORS["text"])
            self.screen.blit(text, (b.rect.centerx - text.get_width() // 2, b.rect.centery - text.get_height() // 2))

        subtitle = self.small.render("WASD: camera · Mouse: interact · TAB: spawn menu · ESC: menu", True, (170, 175, 188))
        self.screen.blit(subtitle, (w // 2 - subtitle.get_width() // 2, h - 36))

    def handle_main_menu_click(self, pos: tuple[int, int]) -> None:
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                b.callback()

    def draw_in_game_ui(self, engine) -> None:
        if self.spawn_open:
            self.draw_spawn_panel(engine)
        self.draw_bottom_bar(engine)
        self.draw_selected_info(engine)

    def draw_spawn_panel(self, engine) -> None:
        panel = pygame.Rect(10, 10, 290, engine.screen.get_height() - 20)
        pygame.draw.rect(self.screen, COLORS["panel_dark"], panel, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["outline"], panel, 2, border_radius=12)

        y = panel.y + 12
        for cat in self.categories:
            r = pygame.Rect(panel.x + 10, y, 126, 30)
            active = cat == self.spawn_category
            pygame.draw.rect(self.screen, COLORS["accent"] if active else COLORS["panel"], r, border_radius=8)
            txt = self.small.render(cat, True, COLORS["text"])
            self.screen.blit(txt, (r.x + 10, r.y + 7))
            if engine.input_state["lmb_pressed"] and r.collidepoint(engine.input_state["mouse_pos"]):
                self.spawn_category = cat
            y += 36

        y += 4
        for item in self.spawn_items[self.spawn_category]:
            r = pygame.Rect(panel.x + 150, y, 130, 30)
            pygame.draw.rect(self.screen, COLORS["panel"], r, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["outline"], r, 1, border_radius=8)
            txt = self.small.render(item, True, COLORS["text"])
            self.screen.blit(txt, (r.x + 8, r.y + 7))
            if engine.input_state["lmb_pressed"] and r.collidepoint(engine.input_state["mouse_pos"]):
                engine.spawn_from_ui(item)
            y += 34

    def draw_bottom_bar(self, engine) -> None:
        w, h = self.screen.get_size()
        rect = pygame.Rect(0, h - 42, w, 42)
        pygame.draw.rect(self.screen, COLORS["panel_dark"], rect)
        pygame.draw.line(self.screen, COLORS["outline"], (0, h - 42), (w, h - 42), 2)

        txt = (
            f"Objects: {len(engine.entities)} | Projectiles: {len(engine.projectiles)} | "
            f"Zoom: {engine.camera.zoom:.2f}x | {'PAUSED' if engine.physics.paused else 'RUNNING'}"
        )
        text = self.small.render(txt, True, COLORS["text"])
        self.screen.blit(text, (12, h - 28))

    def draw_selected_info(self, engine) -> None:
        if not engine.selected:
            return
        e = engine.selected
        info = pygame.Rect(engine.screen.get_width() - 270, 12, 258, 142)
        pygame.draw.rect(self.screen, COLORS["panel_dark"], info, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["outline"], info, 2, border_radius=10)
        lines = [
            f"{e.name}",
            f"HP: {e.hp:.1f}/{e.max_hp:.1f}",
            f"Mass: {e.mass:.2f}",
            f"Material: {e.material}",
            f"State: {'Frozen' if e.frozen else 'Active'}",
            f"Burning: {'Yes' if e.on_fire else 'No'}",
        ]
        for i, line in enumerate(lines):
            t = self.small.render(line, True, COLORS["text"])
            self.screen.blit(t, (info.x + 10, info.y + 10 + i * 20))
