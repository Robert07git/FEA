# src/settings_manager.py
import json
import os

class SettingsManager:
    def __init__(self, filename="data/settings.json"):
        self.filename = filename
        self.default_settings = {
            "username": "",
            "num_questions": 10,
            "timer_enabled": True,
            "dark_mode": True
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.filename):
            self.save_settings(self.default_settings)
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.default_settings

    def save_settings(self, new_settings=None):
        if new_settings:
            self.settings.update(new_settings)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
