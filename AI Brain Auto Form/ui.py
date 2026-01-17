import threading
import re
import customtkinter as ctk
from bot import FormBot
from PIL import Image
from tkinter import filedialog, messagebox
import os
import urllib.request
import webbrowser
from data import DATA_MANAGER

# Setup Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- APP CONFIG ---
CURRENT_VERSION = "1.0"
# ⚠️ REPLACE THESE URLs with your actual text file and download link!
VERSION_CHECK_URL = "https://pastebin.com/raw/YOUR_PASTEBIN_ID" 
DOWNLOAD_URL = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"

# --- Persona Card Component (For Grid) ---
class PersonaCard(ctk.CTkFrame):
    def __init__(self, parent, thread_id):
        super().__init__(parent, corner_radius=15, border_width=2, border_color="#333", fg_color="#1F1F1F")
        self.thread_id = thread_id
        
        self.grid_columnconfigure(1, weight=1)
        
        self.lbl_avatar = ctk.CTkLabel(self, text="👤", font=ctk.CTkFont(size=48))
        self.lbl_avatar.grid(row=0, column=0, rowspan=3, padx=15, pady=10)
        
        self.lbl_name = ctk.CTkLabel(self, text=f"Agent #{thread_id}", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_name.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(15, 0))
        
        self.lbl_role = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=14), text_color="#AAAAAA")
        self.lbl_role.grid(row=1, column=1, sticky="nw", padx=(0, 10))
        
        self.lbl_traits = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="#106EBE")
        self.lbl_traits.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=(5, 15))

    def update_card(self, persona):
        self.lbl_name.configure(text=persona['name'].upper())
        group = DATA_MANAGER.get_group_for_role(persona['role'])
        level = persona.get("level", "General")
        self.lbl_role.configure(text=f"{persona['role']} | {group} | {level} | Age {persona['age']}")
        
        traits = f"{persona.get('personality', '')}"
        if len(traits) > 25: traits = traits[:25] + "..."
        
        self.lbl_traits.configure(text=traits)
        
        # Color coding based on Role Type
        color = "#2CC985" # Default Green
        if "Student" in persona['role'] or "Gamer" in persona['role']: color = "#E04F5F" # Red
        elif "Manager" in persona['role'] or "Officer" in persona['role']: color = "#106EBE" # Blue
        elif "Artist" in persona['role'] or "Creator" in persona['role']: color = "#E0A34F" # Orange
        
        self.configure(border_color=color)
        self.lbl_traits.configure(text_color=color)

        # Avatar
        if persona.get("avatar") and os.path.exists(persona["avatar"]):
            try:
                img = ctk.CTkImage(Image.open(persona["avatar"]), size=(60, 60))
                self.lbl_avatar.configure(image=img, text="")
            except: self.lbl_avatar.configure(image=None, text="👤")
        else: self.lbl_avatar.configure(image=None, text="👤")

# --- Persona Editor Class ---
class PersonaEditor(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Persona Editor")
        self.geometry("400x600")
        self.attributes("-topmost", True)
        self.avatar_path = ""
        
        self.lbl_title = ctk.CTkLabel(self, text="Create / Edit Persona", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=20)
        
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Name")
        self.entry_name.pack(pady=5, padx=20, fill="x")
        
        self.entry_age = ctk.CTkEntry(self, placeholder_text="Age")
        self.entry_age.pack(pady=5, padx=20, fill="x")
        
        self.entry_role = ctk.CTkEntry(self, placeholder_text="Role (e.g. Manager)")
        self.entry_role.pack(pady=5, padx=20, fill="x")
        
        self.entry_traits = ctk.CTkEntry(self, placeholder_text="Traits (e.g. Introvert, Detailed)")
        self.entry_traits.pack(pady=5, padx=20, fill="x")
        
        self.entry_interests = ctk.CTkEntry(self, placeholder_text="Interests (comma separated)")
        self.entry_interests.pack(pady=5, padx=20, fill="x")
        
        self.btn_upload = ctk.CTkButton(self, text="📸 Upload Avatar", command=self.upload_image, fg_color="#E04F5F")
        self.btn_upload.pack(pady=20)
        
        self.lbl_preview = ctk.CTkLabel(self, text="No Image Selected", text_color="gray")
        self.lbl_preview.pack(pady=5)
        
        self.btn_save = ctk.CTkButton(self, text="💾 Save Persona", command=self.save_persona, fg_color="#2CC985")
        self.btn_save.pack(pady=20, padx=20, fill="x")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.avatar_path = file_path
            self.lbl_preview.configure(text=os.path.basename(file_path))

    def save_persona(self):
        name = self.entry_name.get()
        if not name: return
        saved_avatar_path = ""
        if self.avatar_path:
            saved_avatar_path = DATA_MANAGER.save_avatar(self.avatar_path)

        new_persona = {
            "name": name,
            "age": int(self.entry_age.get() or "25"),
            "role": self.entry_role.get() or "Standard User",
            "personality": self.entry_traits.get() or "Neutral",
            "interests": [x.strip() for x in self.entry_interests.get().split(",")],
            "avatar": saved_avatar_path
        }
        DATA_MANAGER.add_persona(new_persona)
        self.destroy()

# --- Group + Position Filter Dialog ---
class GroupPositionDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_groups, current_positions, callback):
        super().__init__(parent)
        self.title("Filter Groups & Positions")
        self.geometry("420x560")
        self.attributes("-topmost", True)
        self.callback = callback

        self.selected_groups = set(current_groups or [])
        self.selected_positions = set(current_positions or [])

        self.lbl_title = ctk.CTkLabel(self, text="Select Target Groups & Positions", font=("Arial", 18, "bold"))
        self.lbl_title.pack(pady=(12, 6))

        # Quick actions (always visible)
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=(0, 8), fill="x")

        self.btn_all = ctk.CTkButton(self.action_frame, text="Select All", width=110, command=self.select_all, fg_color="#555")
        self.btn_all.pack(side="left", padx=(20, 8))

        self.btn_none = ctk.CTkButton(self.action_frame, text="Clear All", width=110, command=self.clear_all, fg_color="#444")
        self.btn_none.pack(side="left", padx=(0, 8))

        self.btn_save = ctk.CTkButton(self.action_frame, text="Save Filter", width=110, command=self.save_selection, fg_color="#2CC985")
        self.btn_save.pack(side="right", padx=(8, 20))

        # Group selection
        self.group_frame = ctk.CTkScrollableFrame(self, width=360, height=140)
        self.group_frame.pack(pady=5, padx=10, fill="x")

        self.group_vars = {}
        self._build_group_checkboxes()

        # Position selection
        self.position_frame = ctk.CTkScrollableFrame(self, width=360, height=200)
        self.position_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.position_vars = {}
        self._refresh_positions()

        # Add position
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.pack(pady=10, padx=10, fill="x")

        self.add_group_var = ctk.StringVar(value=DATA_MANAGER.get_all_group_names()[0])
        self.add_group_menu = ctk.CTkOptionMenu(self.add_frame, values=DATA_MANAGER.get_all_group_names(),
                                                variable=self.add_group_var, width=140)
        self.add_group_menu.pack(side="left", padx=(0, 8))

        self.entry_position = ctk.CTkEntry(self.add_frame, placeholder_text="New position name")
        self.entry_position.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_add_position = ctk.CTkButton(self.add_frame, text="Add", command=self.add_position, width=60)
        self.btn_add_position.pack(side="left")

        # Spacer to keep layout balanced
        self.spacer = ctk.CTkFrame(self, fg_color="transparent")
        self.spacer.pack(pady=4, fill="x")

    def _build_group_checkboxes(self):
        for widget in self.group_frame.winfo_children():
            widget.destroy()

        self.group_vars = {}
        for group in DATA_MANAGER.get_all_group_names():
            var = ctk.StringVar(value=group if group in self.selected_groups or "All" in self.selected_groups else "")
            chk = ctk.CTkCheckBox(self.group_frame, text=group, variable=var, onvalue=group, offvalue="",
                                  command=self._refresh_positions)
            chk.pack(pady=4, padx=10, anchor="w")
            self.group_vars[group] = var

    def _current_groups(self):
        selected = [g for g, var in self.group_vars.items() if var.get()]
        return selected if selected else ["All"]

    def _capture_positions(self):
        for role, var in self.position_vars.items():
            if var.get():
                self.selected_positions.add(role)
            else:
                self.selected_positions.discard(role)

    def _refresh_positions(self):
        self._capture_positions()
        for widget in self.position_frame.winfo_children():
            widget.destroy()

        self.position_vars = {}
        positions = DATA_MANAGER.get_positions_for_groups(self._current_groups())
        for role in positions:
            var = ctk.StringVar(value=role if role in self.selected_positions or "All" in self.selected_positions else "")
            chk = ctk.CTkCheckBox(self.position_frame, text=role, variable=var, onvalue=role, offvalue="")
            chk.pack(pady=4, padx=10, anchor="w")
            self.position_vars[role] = var

    def select_all(self):
        for var in self.group_vars.values():
            var.set(var._on_value)
        self._refresh_positions()
        for var in self.position_vars.values():
            var.set(var._on_value)

    def clear_all(self):
        for var in self.group_vars.values():
            var.set("")
        self._refresh_positions()
        for var in self.position_vars.values():
            var.set("")

    def add_position(self):
        group = self.add_group_var.get()
        position = self.entry_position.get().strip()
        if DATA_MANAGER.add_position_to_group(group, position):
            self.entry_position.delete(0, "end")
            self._refresh_positions()

    def save_selection(self):
        selected_groups = [g for g, var in self.group_vars.items() if var.get()]
        selected_positions = [r for r, var in self.position_vars.items() if var.get()]

        all_groups = list(self.group_vars.keys())
        all_positions = DATA_MANAGER.get_positions_for_groups(selected_groups or ["All"])

        if not selected_groups or len(selected_groups) == len(all_groups):
            selected_groups = ["All"]
        if not selected_positions or len(selected_positions) == len(all_positions):
            selected_positions = ["All"]

        self.callback(selected_groups, selected_positions)
        self.destroy()

# --- Main App ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"AI Form Auto-Filler Pro (Gen 3) - v{CURRENT_VERSION}")
        self.geometry("1280x880") # Expanded for 10 agents + filters
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Auto-Check for Updates (Threaded)
        threading.Thread(target=self.check_for_updates, daemon=True).start()

        self.config = DATA_MANAGER.config
        self.threads = []
        self.cards = {} # thread_id -> PersonaCard

        # --- LEFT SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(13, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="✨ AI BRAIN", font=ctk.CTkFont(size=26, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.lbl_subtitle = ctk.CTkLabel(self.sidebar_frame, text="Genius Mode Enabled", text_color="#2CC985", font=ctk.CTkFont(size=12))
        self.lbl_subtitle.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Inputs
        self.lbl_url = ctk.CTkLabel(self.sidebar_frame, text="Google Form URL:", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_url.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_url = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Paste your link here...")
        self.entry_url.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.entry_url.insert(0, self.config.get("url", ""))

        self.lbl_loop = ctk.CTkLabel(self.sidebar_frame, text="Total Loops:", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_loop.grid(row=4, column=0, padx=20, pady=(8, 0), sticky="w")
        self.entry_loop = ctk.CTkEntry(self.sidebar_frame)
        self.entry_loop.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.entry_loop.insert(0, self.config.get("loops", "5"))

        # Load saved groups/positions or default to All
        self.target_groups = self.config.get("target_groups", ["All"])
        self.target_positions = self.config.get("target_positions", ["All"])

        # Group/Position Filter
        self.filter_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.filter_frame.grid(row=6, column=0, padx=20, pady=(2, 6), sticky="ew")

        self.btn_filter_group = ctk.CTkButton(self.filter_frame, text="Filter Groups & Positions",
                                              command=self.open_group_filter, fg_color="#E0A34F", text_color="#222")
        self.btn_filter_group.pack(fill="x")

        self.lbl_group_status = ctk.CTkLabel(self.filter_frame, text=self.get_group_status_text(),
                                             font=ctk.CTkFont(size=11), text_color="#AAA")
        self.lbl_group_status.pack(pady=2)

        # Forbidden Answers
        self.forbid_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#2A2A2A", corner_radius=8)
        self.forbid_frame.grid(row=7, column=0, padx=15, pady=(4, 8), sticky="ew")

        self.lbl_forbid = ctk.CTkLabel(self.forbid_frame, text="🚫 Forbidden Answers (Exact match)",
                                       font=("Arial", 11, "bold"))
        self.lbl_forbid.pack(pady=(10, 4), padx=10, anchor="w")

        self.text_forbid = ctk.CTkTextbox(self.forbid_frame, height=70, font=("Consolas", 11))
        self.text_forbid.pack(padx=10, pady=(0, 8), fill="x")
        forbidden_seed = "\n".join(self.config.get("forbidden_answers", []))
        if forbidden_seed:
            self.text_forbid.insert("1.0", forbidden_seed)

        self.btn_forbid_apply = ctk.CTkButton(self.forbid_frame, text="Apply Forbidden Answers",
                                              command=self.apply_forbidden_answers, fg_color="#555")
        self.btn_forbid_apply.pack(padx=10, pady=(0, 6), anchor="w")

        self.lbl_forbid_status = ctk.CTkLabel(self.forbid_frame, text="Status: Not applied",
                                              font=("Arial", 10), text_color="#AAA")
        self.lbl_forbid_status.pack(padx=10, pady=(0, 6), anchor="w")

        self.btn_forbid_img = ctk.CTkButton(self.forbid_frame, text="Load Image (OCR)",
                                            command=self.load_forbidden_from_image, fg_color="#444")
        self.btn_forbid_img.pack(padx=10, pady=(0, 8), anchor="w")

        # Forbidden Ages (Rules)
        self.age_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#2A2A2A", corner_radius=8)
        self.age_frame.grid(row=8, column=0, padx=15, pady=(0, 8), sticky="ew")

        self.lbl_age = ctk.CTkLabel(self.age_frame, text="🚫 Forbidden Age Rules",
                                    font=("Arial", 11, "bold"))
        self.lbl_age.pack(pady=(10, 4), padx=10, anchor="w")

        rules = self.config.get("forbidden_age_rules", [])
        legacy_ages = self.config.get("forbidden_ages", [])
        if isinstance(legacy_ages, list):
            for a in legacy_ages:
                rules.append({"type": "eq", "value": a})

        self.var_under18 = ctk.StringVar(value="0")
        self.var_over25 = ctk.StringVar(value="0")
        self.var_over55 = ctk.StringVar(value="0")

        custom_tokens = []
        for rule in rules:
            r_type = rule.get("type")
            val = rule.get("value")
            if r_type == "lt" and val == 18:
                self.var_under18.set("1")
            elif r_type == "gte" and val == 25:
                self.var_over25.set("1")
            elif r_type == "gte" and val == 55:
                self.var_over55.set("1")
            elif r_type == "range":
                custom_tokens.append(f"{rule.get('min')}-{rule.get('max')}")
            elif r_type == "eq":
                custom_tokens.append(str(val))
            elif r_type == "lt":
                custom_tokens.append(f"<{val}")
            elif r_type == "lte":
                custom_tokens.append(f"<={val}")
            elif r_type == "gt":
                custom_tokens.append(f">{val}")
            elif r_type == "gte":
                custom_tokens.append(f">={val}")

        self.chk_under18 = ctk.CTkCheckBox(self.age_frame, text="Under 18", variable=self.var_under18, onvalue="1", offvalue="0")
        self.chk_under18.pack(padx=10, pady=(0, 2), anchor="w")

        self.chk_over25 = ctk.CTkCheckBox(self.age_frame, text="25+ years", variable=self.var_over25, onvalue="1", offvalue="0")
        self.chk_over25.pack(padx=10, pady=(0, 2), anchor="w")

        self.chk_over55 = ctk.CTkCheckBox(self.age_frame, text="55+ years", variable=self.var_over55, onvalue="1", offvalue="0")
        self.chk_over55.pack(padx=10, pady=(0, 6), anchor="w")

        self.entry_age_rules = ctk.CTkEntry(self.age_frame, placeholder_text="Custom: 20-24, <18, >=30")
        self.entry_age_rules.pack(padx=10, pady=(0, 10), fill="x")
        if custom_tokens:
            self.entry_age_rules.insert(0, ", ".join(custom_tokens))

        # Advanced Controls Pannel
        self.adv_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#333", corner_radius=8)
        self.adv_frame.grid(row=9, column=0, padx=15, pady=(0, 8), sticky="ew")
        
        self.lbl_adv = ctk.CTkLabel(self.adv_frame, text="🔧 Advanced Config", font=("Arial", 12, "bold"))
        self.lbl_adv.pack(pady=10)

        self.chk_faker = ctk.CTkCheckBox(self.adv_frame, text="Auto-fill Identity (Faker)", font=("Arial", 11), fg_color="#106EBE")
        self.chk_faker.pack(pady=5, padx=15, anchor="w")
        
        self.chk_headless = ctk.CTkCheckBox(self.adv_frame, text="Ghost Mode (Hide Browser)", font=("Arial", 11), fg_color="#106EBE")
        self.chk_headless.pack(pady=5, padx=15, anchor="w")

        self.lbl_threads = ctk.CTkLabel(self.adv_frame, text="Parallel Agents:", font=("Arial", 11))
        self.lbl_threads.pack(pady=(10,0), padx=15, anchor="w")
        self.slider_threads = ctk.CTkSlider(self.adv_frame, from_=1, to=12, number_of_steps=11, width=180)
        self.slider_threads.set(1)
        self.slider_threads.pack(pady=10, padx=15)
        
        # Display Slider Value
        self.lbl_thread_value = ctk.CTkLabel(self.adv_frame, text="1 Agent", font=("Arial", 10))
        self.lbl_thread_value.pack(pady=(0, 10))
        self.slider_threads.configure(command=self.update_slider_label)

        # Bottom Buttons (always visible)
        self.bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bottom_frame.grid(row=13, column=0, padx=15, pady=(0, 10), sticky="sew")

        self.btn_editor = ctk.CTkButton(self.bottom_frame, text="👥 Manage Personas", command=self.open_editor,
                                        fg_color="#444", hover_color="#555")
        self.btn_editor.pack(fill="x", pady=(0, 8))

        self.btn_start = ctk.CTkButton(self.bottom_frame, text="🚀 START ENGINE", command=self.start_engine, 
                                       fg_color="#106EBE", hover_color="#115EA3", height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_start.pack(fill="x")

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_frame.grid_rowconfigure(0, weight=1) # Grid Area (Auto Height)
        self.main_frame.grid_rowconfigure(1, weight=0) # Log Label (Compact)
        self.main_frame.grid_rowconfigure(2, weight=1) # Log Area (Expands)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 1. Grid Container for Cards
        self.grid_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_container.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        # Initial Placeholder
        self.setup_grid(1)

        # 2. Log Area
        self.lbl_console = ctk.CTkLabel(self.main_frame, text="ACTIVITY LOG", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.lbl_console.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.textbox_log = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), text_color="#00EE00", fg_color="black", height=200)
        self.textbox_log.grid(row=2, column=0, sticky="nsew")

    def update_slider_label(self, value):
        self.lbl_thread_value.configure(text=f"{int(value)} Agent(s)")

    def open_group_filter(self):
        GroupPositionDialog(self, self.target_groups, self.target_positions, self.update_group_selection)

    def update_group_selection(self, selected_groups, selected_positions):
        self.target_groups = selected_groups
        self.target_positions = selected_positions
        self.lbl_group_status.configure(text=self.get_group_status_text())

    def get_group_status_text(self):
        if "All" in self.target_groups and "All" in self.target_positions:
            return "Status: All Groups/Positions"

        group_count = "All" if "All" in self.target_groups else str(len(self.target_groups))
        position_count = "All" if "All" in self.target_positions else str(len(self.target_positions))
        return f"Status: Groups {group_count} | Positions {position_count}"

    def open_editor(self):
        editor = PersonaEditor(self)
        editor.grab_set()

    def setup_grid(self, num_threads):
        # Clear existing
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        self.cards = {}
        
        # Configure dynamic grid
        if num_threads <= 1:
            columns = 1
        elif num_threads <= 4:
            columns = 2
        elif num_threads <= 9:
            columns = 3
        else:
            columns = 4

        rows = (num_threads + columns - 1) // columns

        for c in range(columns):
            self.grid_container.grid_columnconfigure(c, weight=1)
        for r in range(rows):
            self.grid_container.grid_rowconfigure(r, weight=1)

        for i in range(num_threads):
            row = i // columns
            col = i % columns
            card = PersonaCard(self.grid_container, i + 1)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            self.cards[i + 1] = card

    def update_persona_ui(self, thread_id, persona):
        # Use .after to ensure thread safety
        self.after(0, self._update_persona_ui_safe, thread_id, persona)

    def _update_persona_ui_safe(self, thread_id, persona):
        if thread_id in self.cards:
            self.cards[thread_id].update_card(persona)

    def log_message(self, message):
         self.after(0, lambda: self.textbox_log.insert("end", message + "\n"))
         self.after(0, lambda: self.textbox_log.see("end"))

    def start_engine(self):
        url = self.entry_url.get()
        if not url: return
        try: total_loops = int(self.entry_loop.get())
        except: return

        forbidden_answers = self.get_forbidden_answers()
        forbidden_age_rules = self.get_forbidden_age_rules()
        DATA_MANAGER.save_config(
            url,
            str(total_loops),
            self.target_groups,
            self.target_positions,
            forbidden_answers,
            "exact",
            [],
            forbidden_age_rules
        )
        
        # Advanced Configs
        use_faker = bool(self.chk_faker.get())
        headless = bool(self.chk_headless.get())
        num_threads = int(self.slider_threads.get())
        persona_pool = DATA_MANAGER.build_persona_pool(self.target_groups, self.target_positions, num_threads)
        
        # Reset Grid
        self.setup_grid(num_threads)

        self.btn_start.configure(state="disabled", text=f"Running ({num_threads} Threads)...")
        self.log_message(f"🚀 Initializing {num_threads} Parallel Engines...")
        
        # Distribute loops
        loops_per_thread = total_loops // num_threads
        remainder = total_loops % num_threads

        for i in range(num_threads):
            loops = loops_per_thread + (1 if i < remainder else 0)
            if loops > 0:
                persona = persona_pool[i]
                t = threading.Thread(target=self.run_bot_thread, args=(url, loops, headless, use_faker, i+1, persona))
                t.daemon = True
                t.start()
                self.threads.append(t)

    def run_bot_thread(self, url, loops, headless, use_faker, thread_id, persona):
        try:
            bot = FormBot(url, loops, self.log_message, headless, use_faker, thread_id=thread_id, fixed_persona=persona)
            # Use main thread for UI callback to avoid conflicts
            bot.on_persona_change = self.update_persona_ui 
            bot.run()
        except Exception as e:
            self.log_message(f"❌ Thread {thread_id} Error: {e}")
        finally:
            self.log_message(f"🏁 Thread {thread_id} Finished")
            if threading.active_count() <= 2: # Main thread + this ending thread (approx)
                self.after(0, lambda: self.btn_start.configure(state="normal", text="🚀 START ENGINE"))
                self.log_message("✅ All Batches Complete")

    def get_forbidden_answers(self):
        text = self.text_forbid.get("1.0", "end").strip()
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]

    def apply_forbidden_answers(self):
        forbidden = self.get_forbidden_answers()
        if not forbidden:
            self.lbl_forbid_status.configure(text="Status: No entries", text_color="#AAA")
            return
        self.lbl_forbid_status.configure(text=f"Status: Applied {len(forbidden)} items", text_color="#2CC985")

    def get_forbidden_age_rules(self):
        rules = []
        if self.var_under18.get() == "1":
            rules.append({"type": "lt", "value": 18})
        if self.var_over25.get() == "1":
            rules.append({"type": "gte", "value": 25})
        if self.var_over55.get() == "1":
            rules.append({"type": "gte", "value": 55})

        text = self.entry_age_rules.get().strip()
        if not text:
            return rules

        for token in re.split(r"[,\n]+", text):
            t = token.strip()
            if not t:
                continue
            m = re.match(r"^(<=|>=|<|>)\s*(\d{1,3})$", t)
            if m:
                op, num = m.group(1), int(m.group(2))
                if op == "<":
                    rules.append({"type": "lt", "value": num})
                elif op == "<=":
                    rules.append({"type": "lte", "value": num})
                elif op == ">":
                    rules.append({"type": "gt", "value": num})
                elif op == ">=":
                    rules.append({"type": "gte", "value": num})
                continue
            m = re.match(r"^(\d{1,3})\s*[-–]\s*(\d{1,3})$", t)
            if m:
                start = int(m.group(1))
                end = int(m.group(2))
                if start > end:
                    start, end = end, start
                rules.append({"type": "range", "min": start, "max": end})
                continue
            m = re.match(r"^(\d{1,3})$", t)
            if m:
                rules.append({"type": "eq", "value": int(m.group(1))})

        return rules

    def load_forbidden_from_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not file_path:
            return
        try:
            import pytesseract
        except ImportError:
            messagebox.showerror("OCR Not Available", "Please install pytesseract and Tesseract OCR to use this feature.")
            return

        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            messagebox.showerror("OCR Failed", f"Could not read image: {e}")
            return

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            messagebox.showinfo("OCR Result", "No text detected in the image.")
            return

        existing = set(self.get_forbidden_answers())
        new_lines = [l for l in lines if l not in existing]
        if new_lines:
            if existing:
                self.text_forbid.insert("end", "\n" + "\n".join(new_lines))
            else:
                self.text_forbid.insert("1.0", "\n".join(new_lines))

    def check_for_updates(self):
        """Fetches version.txt from server and checks against CURRENT_VERSION"""
        try:
            # Simulated check logic
            if "YOUR_PASTEBIN_ID" in VERSION_CHECK_URL: return # Skip if not configured
            
            with urllib.request.urlopen(VERSION_CHECK_URL, timeout=5) as response:
                latest_version = response.read().decode('utf-8').strip()
                
                # Simple string compare (e.g. "1.1" > "1.0")
                if latest_version > CURRENT_VERSION:
                    self.after(0, self.show_update_popup, latest_version)
        except Exception as e:
            print(f"Update Check Failed: {e}")

    def show_update_popup(self, new_version):
        msg = f"✨ New Version Available: v{new_version}!\n\nYour Version: v{CURRENT_VERSION}\n\nDo you want to download it now?"
        if messagebox.askyesno("Update Available", msg):
            webbrowser.open(DOWNLOAD_URL)

if __name__ == "__main__":
    app = App()
    app.mainloop()
