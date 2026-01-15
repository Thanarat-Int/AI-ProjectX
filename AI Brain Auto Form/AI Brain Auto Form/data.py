import json
import os
import shutil
import sys

# Define default filenames
PERSONAS_FILE_NAME = "personas.json"
CONFIG_FILE_NAME = "config.json"

class DataManager:
    _instance = None
    
    # Singleton Pattern
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.init_init()
        return cls._instance

    def init_init(self):
        """Initialize paths and load data"""
        self.assets_dir = self.resolve_path(os.path.join("assets", "avatars"))
        
        # Ensure avatar dir exists
        if not os.path.exists(self.assets_dir):
            try: os.makedirs(self.assets_dir)
            except: pass

        self.personas = self.load_personas()
        self.config = self.load_config()

    def resolve_path(self, relative_path):
        """
        Get absolute path to resource.
        Works for dev (relative) and PyInstaller (sys._MEIPASS).
        """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def get_user_file(self, filename):
        """
        Get path for user-editable files (next to the .exe).
        We do NOT want these inside sys._MEIPASS because they are read-only there.
        """
        return os.path.join(os.getcwd(), filename)

    def load_personas(self):
        user_path = self.get_user_file(PERSONAS_FILE_NAME)
        
        # 1. Try loading from User's folder (Current Working Directory)
        if os.path.exists(user_path):
            try:
                with open(user_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        
        # 2. Fallback: Load bundled default (Inside EXE)
        bundled_path = self.resolve_path(PERSONAS_FILE_NAME)
        if os.path.exists(bundled_path):
            try:
                with open(bundled_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
            
        return [] # Empty if nothing found

    def save_personas(self):
        # Always save to User's folder
        user_path = self.get_user_file(PERSONAS_FILE_NAME)
        try:
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(self.personas, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving personas: {e}")

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
        try:
            filename = os.path.basename(source_path)
            # Save to user's assets folder, not internal
            user_assets = os.path.join(os.getcwd(), "assets", "avatars")
            if not os.path.exists(user_assets): os.makedirs(user_assets)
            
            dest_path = os.path.join(user_assets, filename)
            shutil.copy(source_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return ""

    def load_config(self):
        user_path = self.get_user_file(CONFIG_FILE_NAME)
        if os.path.exists(user_path):
            try:
                with open(user_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
            
        return {"url": "", "loops": "5"}

    def save_config(self, url, loops):
        self.config = {"url": url, "loops": loops}
        user_path = self.get_user_file(CONFIG_FILE_NAME)
        try:
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except: pass

# Global Instance
DATA_MANAGER = DataManager()
PERSONAS = DATA_MANAGER.personas