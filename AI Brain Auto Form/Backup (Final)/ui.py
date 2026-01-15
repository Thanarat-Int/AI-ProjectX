import threading
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
        
        # Add Group & Level Label
        group = DATA_MANAGER.get_group_for_role(persona['role'])
        level = persona.get('level', 'General')
        # Use vertical pipes and spacing for cleaner look
        self.lbl_role.configure(text=f"{persona['role']}   |   {group}   |   {level}   |   Age {persona['age']}")
        
        traits = f"{persona.get('personality', '')}"
        if len(traits) > 25: traits = traits[:25] + "..."
        
        self.lbl_traits.configure(text=traits)
        
        # Color coding based on Role Type
        color = "#2CC985" # Default Green
        if level == "Executive": color = "#FFD700" # Gold
        elif level == "Manager": color = "#E0A34F" # Orange
        elif level == "Senior": color = "#106EBE" # Blue
        elif level == "Entry": color = "#2CC985" # Green
        elif level == "General": color = "#AAAAAA" # Gray
        
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

# --- Group Filter Dialog (Multi-Select) ---
class GroupFilterDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_selection, callback):
        super().__init__(parent)
        self.title("🎯 Filter Respondent Groups")
        self.geometry("350x500")
        self.attributes("-topmost", True)
        self.callback = callback
        self.params = current_selection if current_selection else ["All"]
        
        self.lbl_title = ctk.CTkLabel(self, text="Select Target Groups", font=("Arial", 18, "bold"))
        self.lbl_title.pack(pady=15)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=300, height=350)
        self.scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.chk_vars = {}
        all_groups = DATA_MANAGER.get_all_group_names()
        
        # Checkbox for each group
        for group in all_groups:
            var = ctk.StringVar(value=group if group in self.params or "All" in self.params else "")
            chk = ctk.CTkCheckBox(self.scroll_frame, text=group, variable=var, onvalue=group, offvalue="")
            chk.pack(pady=5, padx=10, anchor="w")
            self.chk_vars[group] = var

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=20, fill="x")
        
        self.btn_all = ctk.CTkButton(self.btn_frame, text="Select All", width=100, command=self.select_all, fg_color="#555")
        self.btn_all.pack(side="left", padx=20)
        
        self.btn_save = ctk.CTkButton(self.btn_frame, text="✅ Save Filter", width=100, command=self.save_selection, fg_color="#2CC985")
        self.btn_save.pack(side="right", padx=20)

    def select_all(self):
        for var in self.chk_vars.values():
            var.set(var._on_value) # Set to group name

    def save_selection(self):
        selected = []
        for var in self.chk_vars.values():
            if var.get(): selected.append(var.get())
            
        # If all selected or none selected, treat as "All"
        if len(selected) == len(self.chk_vars) or len(selected) == 0:
            selected = ["All"]
            
        self.callback(selected)
        self.destroy()

# --- Main App ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"AI Form Auto-Filler Pro (Gen 3) - v{CURRENT_VERSION}")
        self.geometry("1100x750") # Added width
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Auto-Check for Updates (Threaded)
        threading.Thread(target=self.check_for_updates, daemon=True).start()

        self.config = DATA_MANAGER.config
        self.threads = []
        self.cards = {} # thread_id -> PersonaCard

        # --- LEFT SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

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

        self.entry_loop = ctk.CTkEntry(self.sidebar_frame)
        self.entry_loop.grid(row=5, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.entry_loop.insert(0, self.config.get("loops", "5"))
        
        # Load saved groups or default to All
        self.target_groups = self.config.get("target_groups", ["All"])

        # Group Filter Layout
        self.filter_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.filter_frame.grid(row=6, column=0, padx=20, pady=(5, 5), sticky="ew")
        
        self.btn_filter_group = ctk.CTkButton(self.filter_frame, text="🎯 Filter Groups", command=self.open_group_filter, fg_color="#E0A34F", text_color="#222")
        self.btn_filter_group.pack(fill="x")
        
        self.lbl_group_status = ctk.CTkLabel(self.filter_frame, text=self.get_group_status_text(), font=ctk.CTkFont(size=11), text_color="#AAA")
        self.lbl_group_status.pack(pady=2)

        # Advanced Controls Pannel
        self.adv_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#333", corner_radius=8)
        self.adv_frame.grid(row=7, column=0, padx=15, pady=10, sticky="ew")
        
        self.lbl_adv = ctk.CTkLabel(self.adv_frame, text="🔧 Advanced Config", font=("Arial", 12, "bold"))
        self.lbl_adv.pack(pady=10)

        self.chk_faker = ctk.CTkCheckBox(self.adv_frame, text="Auto-fill Identity (Faker)", font=("Arial", 11), fg_color="#106EBE")
        self.chk_faker.pack(pady=5, padx=15, anchor="w")
        
        self.chk_headless = ctk.CTkCheckBox(self.adv_frame, text="Ghost Mode (Hide Browser)", font=("Arial", 11), fg_color="#106EBE")
        self.chk_headless.pack(pady=5, padx=15, anchor="w")

        self.lbl_threads = ctk.CTkLabel(self.adv_frame, text="Parallel Agents:", font=("Arial", 11))
        self.lbl_threads.pack(pady=(10,0), padx=15, anchor="w")
        self.slider_threads = ctk.CTkSlider(self.adv_frame, from_=1, to=4, number_of_steps=3, width=180)
        self.slider_threads.set(1)
        self.slider_threads.pack(pady=10, padx=15)
        
        # Display Slider Value
        self.lbl_thread_value = ctk.CTkLabel(self.adv_frame, text="1 Agent", font=("Arial", 10))
        self.lbl_thread_value.pack(pady=(0, 10))
        self.slider_threads.configure(command=self.update_slider_label)

        # Bottom Buttons
        self.btn_editor = ctk.CTkButton(self.sidebar_frame, text="👥 Manage Personas", command=self.open_editor, fg_color="#444", hover_color="#555")
        self.btn_editor.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_start = ctk.CTkButton(self.sidebar_frame, text="🚀 START ENGINE", command=self.start_engine, 
                                       fg_color="#106EBE", hover_color="#115EA3", height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_start.grid(row=10, column=0, padx=20, pady=20, sticky="ew")

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_frame.grid_rowconfigure(0, weight=0) # Grid Area (Auto Height)
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
        GroupFilterDialog(self, self.target_groups, self.update_group_selection)

    def update_group_selection(self, selected_groups):
        self.target_groups = selected_groups
        self.lbl_group_status.configure(text=self.get_group_status_text())

    def get_group_status_text(self):
        if "All" in self.target_groups: return "Status: All Groups"
        return f"Status: {len(self.target_groups)} Groups Selected"

    def open_editor(self):
        editor = PersonaEditor(self)
        editor.grab_set()

    def setup_grid(self, num_threads):
        # Clear existing
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        self.cards = {}
        
        # Configure Grid Rows/Cols
        if num_threads == 1:
            self.grid_container.grid_columnconfigure(0, weight=1)
            self.grid_container.grid_rowconfigure(0, weight=1)
            card = PersonaCard(self.grid_container, 1)
            card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.cards[1] = card
        else:
            # 2x2 Grid for 2-4 threads
            self.grid_container.grid_columnconfigure(0, weight=1)
            self.grid_container.grid_columnconfigure(1, weight=1)
            self.grid_container.grid_rowconfigure(0, weight=1)
            self.grid_container.grid_rowconfigure(1, weight=1)
            
            for i in range(num_threads):
                row = i // 2
                col = i % 2
                card = PersonaCard(self.grid_container, i+1)
                card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
                self.cards[i+1] = card

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

        DATA_MANAGER.save_config(url, str(total_loops), self.target_groups)
        
        # Advanced Configs
        use_faker = bool(self.chk_faker.get())
        headless = bool(self.chk_headless.get())
        num_threads = int(self.slider_threads.get())
        
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
                t = threading.Thread(target=self.run_bot_thread, args=(url, loops, headless, use_faker, i+1, self.target_groups))
                t.daemon = True
                t.start()
                self.threads.append(t)

    def run_bot_thread(self, url, loops, headless, use_faker, thread_id, target_groups):
        try:
            bot = FormBot(url, loops, self.log_message, headless, use_faker, thread_id=thread_id, target_groups=target_groups)
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