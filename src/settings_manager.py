import json
import os

SETTINGS_FILE = "data/settings.json"

default_settings = {
    "theme": "dark",
    "time_per_question": 60,
    "num_questions": 10
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
