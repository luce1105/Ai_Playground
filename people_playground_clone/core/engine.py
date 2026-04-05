from __future__ import annotations

import json
import os
import random
import pygame
import pymunk

from config import TITLE, COLORS, DEFAULT_SETTINGS, SETTINGS_PATH
from core.audio import AudioManager
from core.camera import Camera
from core.map_loader import MapLoader
from core.particles import ParticleSystem
from core.physics import PhysicsWorld
from core.save_system import SaveSystem
from core.ui import UIManager
from entities.environment import create_bounds
from entities.effects import FireEmitter
from entities.human import Human
from entities.item import Item
from entities.weapon import Weapon


class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        self.settings = self._load_settings()
        flags = pygame.FULLSCREEN if self.settings.get("fullscreen") else 0
        self.screen = pygame.display.set_mode(self.settings["resolution"], flags)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.ui = UIManager(self.screen)
        self.camera = Camera()
        self.physics = PhysicsWorld()
        self.physics.engine = self
        self.particles = ParticleSystem()
        self.audio = AudioManager(self.settings)
        self.save_system = SaveSystem()
        self.map_loader = MapLoader()

        self.entities: list = []
        self.projectiles: list = []
        self.to_remove: list = []
        self.selected = None

        self.drag_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.drag_joint = None
        self.spawn_cursor = pygame.Vector2(0, 0)
        self.current_map = "sandbox"

        self.input_state = {
            "mouse_pos": (0, 0),
            "lmb": False,
            "rmb": False,
            "lmb_pressed": False,
            "rmb_pressed": False,
        }

        self._setup_handlers()
        self.ui.build_main_menu(self.screen.get_size(), {
            "play": self.start_game,
            "settings": self.toggle_settings,
            "sandbox": self.start_game,
            "load": self.load_latest,
            "quit": self.quit_game,
        })

    def _load_settings(self) -> dict:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        if not os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2)
            return dict(DEFAULT_SETTINGS)
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = dict(DEFAULT_SETTINGS)
        out.update(data)
        return out

    def _save_settings(self) -> None:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)

    def _setup_handlers(self) -> None:
        h = self.physics.space.add_collision_handler(2, 1)
        h.post_solve = self._on_projectile_hit

    def _on_projectile_hit(self, arbiter, space, data):
        a, b = arbiter.shapes
        proj = getattr(a, "entity_ref", None)
        target = getattr(b, "entity_ref", None)
        if proj is None:
            proj = getattr(b, "entity_ref", None)
            target = getattr(a, "entity_ref", None)
        if proj and proj in self.projectiles:
            if target and hasattr(target, "apply_damage"):
                pos = arbiter.contact_point_set.points[0].point_a
                target.apply_damage(proj.damage, (pos.x, pos.y))
                if hasattr(target, "body"):
                    target.body.apply_impulse_at_world_point(proj.body.velocity * proj.damage * 0.015, pos)
                self.particles.emit((pos.x, pos.y), 5, (222, 222, 222), speed=80, spread=60, size=2, lifetime=0.25)
            proj.destroy()
        return True

    def start_game(self) -> None:
        self.state = "game"
        self.reset_world()
        self.load_map("sandbox")

    def toggle_settings(self) -> None:
        self.settings["show_blood"] = not self.settings["show_blood"]
        self._save_settings()

    def load_latest(self) -> None:
        saves = self.save_system.list_saves()
        if not saves:
            self.start_game()
            return
        self.start_game()
        self.load_scene(saves[-1])

    def quit_game(self) -> None:
        self.running = False

    def reset_world(self):
        self.physics = PhysicsWorld()
        self.physics.engine = self
        self.entities.clear()
        self.projectiles.clear()
        self.to_remove.clear()
        self._setup_handlers()
        create_bounds(self.physics.space, 4500, 2500)

    def load_map(self, map_name: str) -> None:
        self.current_map = map_name
        data = self.map_loader.load(map_name)
        for obj in data.get("objects", []):
            self.spawn_object(obj["id"], tuple(obj["pos"]))

    def save_scene(self, slot: str = "slot1") -> None:
        self.save_system.save_scene(slot, self.current_map, self.entities)

    def load_scene(self, slot: str = "slot1") -> None:
        payload = self.save_system.load_scene(slot)
        if not payload:
            return
        self.reset_world()
        self.load_map(payload.get("map", "sandbox"))
        for e in payload.get("entities", []):
            self.spawn_object_from_data(e)

    def spawn_object_from_data(self, data: dict) -> None:
        obj = self.spawn_object(data.get("name", data.get("type", "Wood Crate")), tuple(data.get("pos", (0, 0))))
        if not obj:
            return
        if hasattr(obj, "body"):
            obj.body.angle = data.get("angle", 0)
        if hasattr(obj, "hp"):
            obj.hp = data.get("hp", obj.max_hp)
        if data.get("on_fire") and hasattr(obj, "ignite"):
            obj.ignite()

    def spawn_object(self, item_name: str, pos: tuple[float, float]):
        e = None
        if item_name in ("Human",):
            e = Human(self.physics.space, pos)
        elif item_name in ("Pistol", "Rifle", "Shotgun"):
            e = Weapon(self.physics.space, item_name, pos, item_name.lower())
        elif item_name in ("Wood Crate", "ящик"):
            e = Item(self.physics.space, "Wood Crate", pos, (56, 56), "wood")
        elif item_name in ("Metal Block",):
            e = Item(self.physics.space, "Metal Block", pos, (58, 38), "metal")
        elif item_name in ("Glass Panel",):
            e = Item(self.physics.space, "Glass Panel", pos, (74, 16), "glass", COLORS["glass"])
        elif item_name in ("Stone Brick", "Brick"):
            e = Item(self.physics.space, "Stone Brick", pos, (64, 24), "stone")
        elif item_name in ("Rubber Wheel",):
            e = Item(self.physics.space, "Rubber Wheel", pos, (40, 40), "rubber")
        elif item_name in ("Explosive Barrel", "Barrel"):
            e = Item(self.physics.space, "Explosive Barrel", pos, (40, 62), "metal", (167, 77, 47))
        elif item_name == "Fire Emitter":
            e = FireEmitter(self.physics.space, pygame.Vector2(pos))
        elif item_name == "Lamp":
            e = Item(self.physics.space, "Lamp", pos, (16, 52), "metal", (255, 237, 164))
        elif item_name == "Door":
            e = Item(self.physics.space, "Door", pos, (26, 94), "wood")
        elif item_name == "Platform":
            e = Item(self.physics.space, "Platform", pos, (140, 18), "metal")
        elif item_name == "Spike":
            e = Item(self.physics.space, "Spike", pos, (16, 28), "metal", (193, 198, 207))
        else:
            e = Item(self.physics.space, item_name, pos, (50, 50), random.choice(["wood", "metal", "stone"]))

        self.entities.append(e)
        return e

    def spawn_from_ui(self, item_name: str) -> None:
        world_pos = self.camera.screen_to_world(self.input_state["mouse_pos"], self.screen.get_size())
        self.spawn_object(item_name, tuple(world_pos))

    def pick_entity(self, screen_pos: tuple[int, int]):
        world = self.camera.screen_to_world(screen_pos, self.screen.get_size())
        hit = self.physics.space.point_query_nearest(world, 2, pymunk.ShapeFilter())
        if hit and hasattr(hit.shape, "entity_ref"):
            return hit.shape.entity_ref
        return None

    def handle_events(self) -> None:
        self.input_state["lmb_pressed"] = False
        self.input_state["rmb_pressed"] = False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.MOUSEWHEEL:
                self.camera.add_zoom(ev.y * 0.07)
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    self.input_state["lmb_pressed"] = True
                    self.input_state["lmb"] = True
                if ev.button == 3:
                    self.input_state["rmb_pressed"] = True
                    self.input_state["rmb"] = True
            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    self.input_state["lmb"] = False
                    self.drag_joint = None
                if ev.button == 3:
                    self.input_state["rmb"] = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.state = "menu" if self.state == "game" else "game"
                if ev.key == pygame.K_TAB:
                    self.ui.spawn_open = not self.ui.spawn_open
                if ev.key == pygame.K_SPACE:
                    self.physics.paused = not self.physics.paused
                if ev.key == pygame.K_DELETE and self.selected:
                    self.selected.destroy()
                if ev.key == pygame.K_r and self.selected:
                    self.selected.rotate(15)
                if ev.key == pygame.K_f and self.selected:
                    self.selected.toggle_freeze()
                if ev.key == pygame.K_g and self.selected:
                    self.selected.toggle_gravity()
                if ev.key == pygame.K_e and self.selected and hasattr(self.selected, "ignite"):
                    self.selected.ignite()
                if ev.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_scene("slot1")
                if ev.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.load_scene("slot1")

        self.input_state["mouse_pos"] = pygame.mouse.get_pos()

        if self.state == "menu" and self.input_state["lmb_pressed"]:
            self.ui.handle_main_menu_click(self.input_state["mouse_pos"])

        if self.state != "game":
            return

        if self.input_state["lmb_pressed"]:
            self.selected = self.pick_entity(self.input_state["mouse_pos"])
            if self.selected and hasattr(self.selected, "body"):
                world = self.camera.screen_to_world(self.input_state["mouse_pos"], self.screen.get_size())
                self.drag_body.position = world
                self.drag_joint = pymunk.PivotJoint(self.drag_body, self.selected.body, (0, 0), (0, 0))
                self.drag_joint.max_force = 50000
                self.physics.space.add(self.drag_joint)

        if self.drag_joint and self.input_state["lmb"]:
            world = self.camera.screen_to_world(self.input_state["mouse_pos"], self.screen.get_size())
            self.drag_body.position = world

        if self.input_state["rmb_pressed"] and self.selected and isinstance(self.selected, Weapon):
            world = self.camera.screen_to_world(self.input_state["mouse_pos"], self.screen.get_size())
            self.selected.shoot_at(tuple(world))

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.camera.update(dt, keys, self.settings)
        if self.state != "game":
            return

        self.physics.step(dt)

        for e in self.entities:
            e.update(dt)
        for p in self.projectiles:
            p.update(dt)
        self.particles.update(dt)

        if self.drag_joint and not self.input_state["lmb"]:
            if self.drag_joint in self.physics.space.constraints:
                self.physics.space.remove(self.drag_joint)
            self.drag_joint = None

        while self.to_remove:
            e = self.to_remove.pop()
            if e in self.entities:
                self.entities.remove(e)
            if e in self.projectiles:
                self.projectiles.remove(e)
            if hasattr(e, "shape") and hasattr(e, "body"):
                if e.shape in self.physics.space.shapes:
                    self.physics.space.remove(e.shape)
                if e.body in self.physics.space.bodies:
                    self.physics.space.remove(e.body)

    def draw_world(self) -> None:
        self.screen.fill(COLORS["bg"])
        grid = 80
        sw, sh = self.screen.get_size()
        left_top = self.camera.screen_to_world((0, 0), (sw, sh))
        right_bottom = self.camera.screen_to_world((sw, sh), (sw, sh))

        sx = int(left_top.x // grid) * grid
        ex = int(right_bottom.x // grid + 1) * grid
        sy = int(left_top.y // grid) * grid
        ey = int(right_bottom.y // grid + 1) * grid

        for x in range(sx, ex + 1, grid):
            a = self.camera.world_to_screen((x, sy), (sw, sh))
            b = self.camera.world_to_screen((x, ey), (sw, sh))
            pygame.draw.line(self.screen, (38, 42, 50), a, b, 1)
        for y in range(sy, ey + 1, grid):
            a = self.camera.world_to_screen((sx, y), (sw, sh))
            b = self.camera.world_to_screen((ex, y), (sw, sh))
            pygame.draw.line(self.screen, (38, 42, 50), a, b, 1)

        for e in self.entities:
            e.draw(self.screen, self.camera, (sw, sh))
        for p in self.projectiles:
            p.draw(self.screen, self.camera, (sw, sh))
        self.particles.draw(self.screen, self.camera, (sw, sh))

        if self.selected and hasattr(self.selected, "body"):
            s = self.camera.world_to_screen(self.selected.body.position, (sw, sh))
            pygame.draw.circle(self.screen, COLORS["accent"], (int(s.x), int(s.y)), max(12, int(24 * self.camera.zoom)), 2)

    def run(self) -> None:
        while self.running:
            dt = min(1 / 30, self.clock.tick(self.settings.get("fps_limit", 120)) / 1000)
            self.handle_events()
            self.update(dt)

            if self.state == "menu":
                self.ui.draw_main_menu(dt, self.input_state["mouse_pos"])
            else:
                self.draw_world()
                self.ui.draw_in_game_ui(self)

            pygame.display.flip()

        self._save_settings()
        pygame.quit()
