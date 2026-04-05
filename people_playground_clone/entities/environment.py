from __future__ import annotations

import pymunk


def create_bounds(world, width: int, height: int) -> None:
    static = world.space.static_body
    segs = [
        pymunk.Segment(static, (-width / 2, height / 2), (width / 2, height / 2), 18),
        pymunk.Segment(static, (-width / 2, -height / 2), (width / 2, -height / 2), 18),
        pymunk.Segment(static, (-width / 2, -height / 2), (-width / 2, height / 2), 18),
        pymunk.Segment(static, (width / 2, -height / 2), (width / 2, height / 2), 18),
    ]
    for s in segs:
        s.friction = 0.95
        s.elasticity = 0.1
    world.add(*segs)
