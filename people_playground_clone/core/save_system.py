from __future__ import annotations

import json
import os
from config import SAVES_DIR


class SaveSystem:
    def __init__(self) -> None:
        os.makedirs(SAVES_DIR, exist_ok=True)

    def save_scene(self, slot: str, map_name: str, entities: list) -> str:
        path = os.path.join(SAVES_DIR, f"{slot}.json")
        payload = {
            "map": map_name,
            "entities": [e.to_dict() for e in entities if getattr(e, "serializable", True)],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return path

    def load_scene(self, slot: str) -> dict | None:
        path = os.path.join(SAVES_DIR, f"{slot}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_saves(self) -> list[str]:
        return sorted([f[:-5] for f in os.listdir(SAVES_DIR) if f.endswith(".json")])
