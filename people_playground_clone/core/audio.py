from __future__ import annotations

import pygame


class AudioManager:
    def __init__(self, settings: dict) -> None:
        self.enabled = True
        self.settings = settings
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init()
        except pygame.error:
            self.enabled = False

    def register_placeholder(self, name: str) -> None:
        self.sounds[name] = None  # type: ignore[assignment]

    def play(self, name: str, volume_mul: float = 1.0) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        sound.set_volume(self.settings.get("master_volume", 0.7) * volume_mul)
        sound.play()
