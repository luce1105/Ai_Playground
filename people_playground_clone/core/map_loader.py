from __future__ import annotations

import json
import os
from config import MAPS_DIR


class MapLoader:
    def __init__(self) -> None:
        os.makedirs(MAPS_DIR, exist_ok=True)

    def list_maps(self) -> list[str]:
        return sorted([f[:-5] for f in os.listdir(MAPS_DIR) if f.endswith('.json')])

    def load(self, name: str) -> dict:
        path = os.path.join(MAPS_DIR, f"{name}.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
