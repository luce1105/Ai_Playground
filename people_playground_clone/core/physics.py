from __future__ import annotations

import pymunk


class PhysicsWorld:
    def __init__(self) -> None:
        self.space = pymunk.Space()
        self.space.gravity = (0, 980)
        self.paused = False

    def step(self, dt: float) -> None:
        if self.paused:
            return
        fixed_steps = 2
        sub_dt = dt / fixed_steps
        for _ in range(fixed_steps):
            self.space.step(sub_dt)

    def set_gravity(self, enabled: bool) -> None:
        self.space.gravity = (0, 980) if enabled else (0, 0)

    def add(self, *objs) -> None:
        self.space.add(*objs)

    def remove(self, *objs) -> None:
        safe = [o for o in objs if o in self.space]
        if safe:
            self.space.remove(*safe)
