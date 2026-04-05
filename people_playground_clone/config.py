import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVES_DIR = os.path.join(DATA_DIR, "saves")
MAPS_DIR = os.path.join(DATA_DIR, "maps")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "master_volume": 0.7,
    "fullscreen": False,
    "fps_limit": 120,
    "show_blood": True,
    "particle_quality": 1.0,
    "resolution": [1600, 900],
    "camera_sensitivity": 1.0,
    "vsync": False,
}

TITLE = "People Playground Clone"
VERSION = "1.0.0"

COLORS = {
    "bg": (27, 31, 38),
    "panel": (33, 38, 47),
    "panel_dark": (23, 27, 34),
    "text": (234, 238, 245),
    "accent": (84, 156, 255),
    "accent_hover": (111, 176, 255),
    "danger": (217, 86, 86),
    "success": (82, 184, 120),
    "warning": (221, 168, 68),
    "outline": (60, 67, 79),
    "glass": (149, 208, 255),
    "wood": (150, 105, 62),
    "metal": (175, 182, 192),
    "stone": (110, 113, 122),
    "rubber": (70, 74, 79),
    "flesh": (210, 151, 143),
}

MATERIALS = {
    "wood": {
        "density": 0.8,
        "friction": 0.8,
        "elasticity": 0.2,
        "hp": 85,
        "break_impulse": 1300,
        "flammable": 1.0,
        "conductive": 0.1,
    },
    "metal": {
        "density": 2.1,
        "friction": 0.6,
        "elasticity": 0.1,
        "hp": 190,
        "break_impulse": 3500,
        "flammable": 0.0,
        "conductive": 0.9,
    },
    "glass": {
        "density": 0.7,
        "friction": 0.4,
        "elasticity": 0.05,
        "hp": 36,
        "break_impulse": 520,
        "flammable": 0.0,
        "conductive": 0.2,
    },
    "stone": {
        "density": 2.5,
        "friction": 0.9,
        "elasticity": 0.04,
        "hp": 220,
        "break_impulse": 3800,
        "flammable": 0.0,
        "conductive": 0.05,
    },
    "rubber": {
        "density": 1.1,
        "friction": 1.2,
        "elasticity": 0.75,
        "hp": 130,
        "break_impulse": 2100,
        "flammable": 0.2,
        "conductive": 0.02,
    },
    "flesh": {
        "density": 1.0,
        "friction": 0.75,
        "elasticity": 0.2,
        "hp": 110,
        "break_impulse": 980,
        "flammable": 0.35,
        "conductive": 0.5,
    },
}

COLLISION_TYPES = {
    "default": 1,
    "projectile": 2,
    "character": 3,
    "sensor": 4,
    "fire": 5,
}

LAYER_ORDER = {
    "background": 0,
    "terrain": 10,
    "object": 20,
    "character": 30,
    "particles": 40,
    "ui": 100,
}
