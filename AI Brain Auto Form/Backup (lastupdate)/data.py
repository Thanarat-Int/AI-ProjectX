import json
import os
import shutil

PERSONAS_FILE = "personas.json"
CONFIG_FILE = "config.json"
AVATAR_DIR = os.path.join("assets", "avatars")

class DataManager:
    def __init__(self):
        # Create avatars dir if not exists
        if not os.path.exists(AVATAR_DIR):
            os.makedirs(AVATAR_DIR)
        
        self.personas = self.load_personas()
        self.config = self.load_config()

    def load_personas(self):
        if not os.path.exists(PERSONAS_FILE):
            return []
        try:
            with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def save_personas(self):
        with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.personas, f, indent=4, ensure_ascii=False)

    def add_persona(self, persona):
        self.personas.append(persona)
        self.save_personas()

    def delete_persona(self, index):
        if 0 <= index < len(self.personas):
            self.personas.pop(index)
            self.save_personas()

    def save_avatar(self, source_path):
        """Copies image to assets/avatars and returns relative path"""
        if not source_path: return ""
        
        filename = os.path.basename(source_path)
        dest_path = os.path.join(AVATAR_DIR, filename)
        
        try:
            shutil.copy(source_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return ""

    # --- Config Section ---
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {"url": "", "loops": "5"}
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"url": "", "loops": "5"}

    def save_config(self, url, loops):
        self.config = {"url": url, "loops": loops}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

# Global Instance
DATA_MANAGER = DataManager()
PERSONAS = DATA_MANAGER.personas # Compatibility alias