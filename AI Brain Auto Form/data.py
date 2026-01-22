import json
import os
import random
import shutil
import sys

from keyword_weights import DEFAULT_INTERESTS

# Define default filenames
PERSONAS_FILE_NAME = "personas.json"
CONFIG_FILE_NAME = "config.json"
GROUPS_FILE_NAME = "groups.json"

# --- DEFAULT GROUPS & POSITIONS ---
DEFAULT_GROUPS = {
    "IT": ["SA", "QA", "Programmer", "Tester", "BA", "IT Support", "Engineer", "Programmer"],
    "Marketing": ["Marketing", "Content Creator", "YouTuber", "Graphic Designer", "Journalist", "Photographer"],
    "Finance": ["Accountant", "Sales Manager", "Small Business Owner", "Real Estate Agent", "Manager", "Start-up Owner", "CFO"],
    "HR": ["HR Specialist"],
    "Healthcare": ["Retired Doctor", "Nurse", "Pharmacist", "Hospital Director"],
    "Services": ["Receptionist", "Call Center", "Flight Attendant", "Taxi Driver", "Shopkeeper", "Gardener", "Chef", "Fitness Trainer"],
    "Education": ["Teacher", "Student", "University Student", "High School Student", "Intern", "School Principal"],
    "General": ["Government Official", "Police Officer", "Housewife", "Freelance"]
}

DEFAULT_PERSONALITY_TRAITS = [
    "Analytical", "Creative", "Detail-oriented", "Calm", "Energetic",
    "Curious", "Practical", "Friendly", "Disciplined", "Ambitious",
    "Introverted", "Extroverted", "Cautious", "Optimistic", "Serious"
]

DEFAULT_VALUES = [
    "Accuracy", "Speed", "Stability", "Innovation", "Efficiency",
    "Security", "Quality", "Growth", "Discipline", "Freedom"
]

DEFAULT_STYLES = ["Formal", "Casual", "Polite", "Direct", "Expressive", "Brief"]
DEFAULT_LEVELS = ["Entry", "Senior", "Manager", "Executive", "General"]

NAME_POOL = [
    "Alex", "Jordan", "Taylor", "Sam", "Chris", "Jamie",
    "Morgan", "Avery", "Casey", "Riley", "Cameron", "Drew"
]

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
        self.groups = self.load_groups()

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

    def load_groups(self):
        user_path = self.get_user_file(GROUPS_FILE_NAME)

        if os.path.exists(user_path):
            try:
                with open(user_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass

        bundled_path = self.resolve_path(GROUPS_FILE_NAME)
        if os.path.exists(bundled_path):
            try:
                with open(bundled_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass

        return DEFAULT_GROUPS.copy()

    def save_personas(self):
        # Always save to User's folder
        user_path = self.get_user_file(PERSONAS_FILE_NAME)
        try:
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(self.personas, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving personas: {e}")

    def save_groups(self):
        user_path = self.get_user_file(GROUPS_FILE_NAME)
        try:
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(self.groups, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving groups: {e}")

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
            
        return {
            "url": "",
            "loops": "5",
            "target_groups": ["All"],
            "target_positions": ["All"],
            "forbidden_answers": [],
            "forbidden_match_mode": "exact",
            "forbidden_ages": [],
            "forbidden_age_rules": [],
            "positive_lock": False
        }

    def save_config(self, url, loops, target_groups=None, target_positions=None, forbidden_answers=None, forbidden_match_mode=None, forbidden_ages=None, forbidden_age_rules=None, positive_lock=None):
        self.config = {"url": url, "loops": loops}
        if target_groups:
            self.config["target_groups"] = target_groups
        if target_positions:
            self.config["target_positions"] = target_positions
        if forbidden_answers is not None:
            self.config["forbidden_answers"] = forbidden_answers
        if forbidden_match_mode is not None:
            self.config["forbidden_match_mode"] = forbidden_match_mode
        if forbidden_ages is not None:
            self.config["forbidden_ages"] = forbidden_ages
        if forbidden_age_rules is not None:
            self.config["forbidden_age_rules"] = forbidden_age_rules
        if positive_lock is not None:
            self.config["positive_lock"] = positive_lock
        user_path = self.get_user_file(CONFIG_FILE_NAME)
        try:
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except: pass

    def add_position_to_group(self, group_name, position_name):
        position_name = position_name.strip()
        if not position_name:
            return False

        if group_name not in self.groups:
            self.groups[group_name] = []

        if position_name not in self.groups[group_name]:
            self.groups[group_name].append(position_name)
            self.save_groups()
        return True

    def get_all_group_names(self):
        return list(self.groups.keys())

    def get_positions_for_groups(self, group_names):
        if not group_names or "All" in group_names:
            all_positions = []
            for roles in self.groups.values():
                all_positions.extend(roles)
            return sorted(set(all_positions))

        positions = []
        for g in group_names:
            positions.extend(self.groups.get(g, []))
        return sorted(set(positions))

    def get_personas_by_filter(self, group_names=None, position_names=None):
        if not group_names or "All" in group_names:
            group_names = ["All"]
        if not position_names or "All" in position_names:
            position_names = ["All"]

        if "All" in group_names and "All" in position_names:
            return self.personas

        allowed_positions = set()
        if "All" in position_names:
            allowed_positions.update(self.get_positions_for_groups(group_names))
        else:
            allowed_positions.update(position_names)

        return [p for p in self.personas if p.get("role") in allowed_positions]

    def get_group_for_role(self, role):
        for group, roles in self.groups.items():
            if any(r.lower() in role.lower() for r in roles):
                return group
        return "General"

    def _random_personality(self):
        traits = random.sample(DEFAULT_PERSONALITY_TRAITS, k=2)
        return ", ".join(traits)

    def _random_interests(self):
        return random.sample(DEFAULT_INTERESTS, k=3)

    def _random_values(self):
        return random.sample(DEFAULT_VALUES, k=2)

    def _random_name(self, used_names):
        base = random.choice(NAME_POOL)
        name = base
        suffix = 1
        while name in used_names:
            suffix += 1
            name = f"{base}{suffix}"
        return name

    def generate_persona(self, role, used_names=None):
        if used_names is None:
            used_names = set()
        name = self._random_name(used_names)
        return {
            "name": name,
            "age": random.randint(20, 55),
            "role": role,
            "level": random.choice(DEFAULT_LEVELS),
            "personality": self._random_personality(),
            "interests": self._random_interests(),
            "values": self._random_values(),
            "style": random.choice(DEFAULT_STYLES)
        }

    def build_persona_pool(self, group_names, position_names, count):
        base = self.get_personas_by_filter(group_names, position_names)

        unique = {}
        for p in base:
            name = p.get("name")
            if name and name not in unique:
                unique[name] = p

        pool = list(unique.values())
        if len(pool) >= count:
            return random.sample(pool, k=count)

        # Generate synthetic personas to guarantee uniqueness
        used_names = set(unique.keys())
        if position_names and "All" not in position_names:
            role_pool = position_names
        else:
            role_pool = self.get_positions_for_groups(group_names)
        if not role_pool:
            role_pool = [p.get("role", "General") for p in self.personas] or ["General"]

        while len(pool) < count:
            role = random.choice(role_pool)
            persona = self.generate_persona(role, used_names)
            used_names.add(persona["name"])
            pool.append(persona)

        return pool

# Global Instance
DATA_MANAGER = DataManager()
PERSONAS = DATA_MANAGER.personas
