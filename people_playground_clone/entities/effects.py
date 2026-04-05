from __future__ import annotations


class FireEmitter:
    def __init__(self, world, pos):
        self.world = world
        self.pos = pos
        self.name = "Fire Emitter"
        self.serializable = True
        self.hp = self.max_hp = 999
        self.mass = 0
        self.material = "metal"
        self.frozen = False
        self.on_fire = False

    @property
    def body(self):
        class Dummy: ...
        d = Dummy()
        d.position = self.pos
        d.angle = 0
        return d

    def update(self, dt: float):
        self.world.engine.particles.emit(self.pos, 2, (255, 142, 36), speed=55, spread=34, size=2.5, lifetime=0.5, gravity=-20)
        for e in self.world.engine.entities:
            if hasattr(e, "ignite") and (e.body.position - self.pos).length < 80:
                e.ignite()

    def draw(self, surf, camera, size):
        p = camera.world_to_screen(self.pos, size)
        import pygame
        pygame.draw.circle(surf, (255, 120, 40), (int(p.x), int(p.y)), max(2, int(9 * camera.zoom)), 2)

    def rotate(self, angle_deg: float):
        pass

    def toggle_freeze(self):
        pass

    def toggle_gravity(self):
        pass

    def destroy(self):
        self.world.engine.to_remove.append(self)

    def to_dict(self):
        return {"type": "FireEmitter", "pos": [self.pos.x, self.pos.y]}
