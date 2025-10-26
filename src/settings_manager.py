import json
import os

SETTINGS_PATH = os.path.join("data", "settings.json")

default_settings = {
    "username": "Guest",
    "dark_mode": True,
    "num_questions": 10
}

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        save_settings(default_settings)
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
