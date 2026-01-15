import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import threading
from analyzer import TrafficAnalyzer

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TrafficApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Smart Traffic Analytics (AI OpenCV)")
        self.geometry("1280x720")

        # Initialize Logic
        self.analyzer = TrafficAnalyzer()
        self.cap = None
        self.is_running = False
        self.video_path = None

        # Grid layout (2 columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === Sidebar (Controls) ===
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Traffic AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_import = ctk.CTkButton(self.sidebar, text="Import Video", command=self.open_file_dialog)
        self.btn_import.grid(row=1, column=0, padx=20, pady=10)

        self.btn_start = ctk.CTkButton(self.sidebar, text="Start Analysis", fg_color="green", command=self.start_analysis)
        self.btn_start.grid(row=2, column=0, padx=20, pady=10)

        self.btn_stop = ctk.CTkButton(self.sidebar, text="Stop", fg_color="red", command=self.stop_analysis)
        self.btn_stop.grid(row=3, column=0, padx=20, pady=10)

        # Status / Counters
        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: Ready", anchor="w")
        self.status_label.grid(row=5, column=0, padx=20, pady=(10, 5))

        # Dashboard Area
        self.dashboard_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.dashboard_frame.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        
        self.label_total = ctk.CTkLabel(self.dashboard_frame, text="Total: 0", font=("Arial", 16, "bold"))
        self.label_total.pack(anchor="w")
        
        self.label_car = ctk.CTkLabel(self.dashboard_frame, text="Cars: 0", font=("Arial", 12))
        self.label_car.pack(anchor="w")
        
        self.label_bus = ctk.CTkLabel(self.dashboard_frame, text="Buses: 0", font=("Arial", 12))
        self.label_bus.pack(anchor="w")
        
        self.label_truck = ctk.CTkLabel(self.dashboard_frame, text="Trucks: 0", font=("Arial", 12))
        self.label_truck.pack(anchor="w")
        
        # === Main Area (Video Display) ===
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Canvas for video
        self.canvas_label = ctk.CTkLabel(self.display_frame, text="Please import a video to start", font=ctk.CTkFont(size=16))
        self.canvas_label.pack(expand=True, fill="both")

    def open_file_dialog(self):
        filename = filedialog.askopenfilename(title="Select Video", filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))
        if filename:
            self.video_path = filename
            self.status_label.configure(text=f"Selected: {filename.split('/')[-1]}")
            # Show preview
            self.show_preview()

    def show_preview(self):
        """Display the first frame of the selected video as a preview."""
        if not self.video_path:
            return
            
        try:
            temp_cap = cv2.VideoCapture(self.video_path)
            ret, frame = temp_cap.read()
            temp_cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_image(frame_rgb)
                self.canvas_label.configure(text="") # Clear text
            else:
                self.status_label.configure(text="Error: Could not read video file.")
        except Exception as e:
            print(f"Error in preview: {e}")
            self.status_label.configure(text=f"Error: {e}")

    def start_analysis(self):
        if not self.video_path:
            self.status_label.configure(text="Error: No video selected!")
            return
        
        if self.is_running:
            return

        print(f"Starting analysis on: {self.video_path}")
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
             print("Error: VideoCapture could not open the file.")
             self.status_label.configure(text="Error: Could not open video.")
             return

        self.is_running = True
        self.status_label.configure(text="Status: Running...")
        
        # Start update loop
        self.update_video()

    def stop_analysis(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.status_label.configure(text="Status: Stopped")
        
        # Reload preview when stopped
        self.show_preview()

    def update_video(self):
        if not self.is_running or not self.cap:
            return

        try:
            ret, frame = self.cap.read()
            if ret:
                # 1. Process frame with AI
                annotated_frame = self.analyzer.process_frame(frame)

                # 2. Convert and Display
                frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                self.display_image(frame_rgb)
                
                # 3. Update Dashboard
                counts = self.analyzer.get_counts()
                self.label_total.configure(text=f"Total: {counts['total']}")
                self.label_car.configure(text=f"Cars: {counts.get('car', 0)}")
                self.label_bus.configure(text=f"Buses: {counts.get('bus', 0)}")
                self.label_truck.configure(text=f"Trucks: {counts.get('truck', 0)}")
                
                # Use .after() to schedule next frame
                self.after(10, self.update_video) # Faster update check
            else:
                print("Video finished or failed to read frame.")
                self.stop_analysis()
                self.status_label.configure(text="Status: Finished")
        except Exception as e:
            print(f"Error in update_loop: {e}")
            self.stop_analysis()
            self.status_label.configure(text=f"Error: {e}")

    def display_image(self, frame_rgb):
        """Helper to resize and display an RGB frame on the canvas label."""
        # Get current display area size
        display_w = self.display_frame.winfo_width()
        display_h = self.display_frame.winfo_height()
        
        # Default fallback if window not fully drawn yet
        if display_w < 50: display_w = 640
        if display_h < 50: display_h = 480

        img = Image.fromarray(frame_rgb)
        
        # Resize image to fit the container maintaining aspect ratio
        img_ratio = img.width / img.height
        target_width = display_w
        target_height = int(target_width / img_ratio)
        
        if target_height > display_h:
            target_height = display_h
            target_width = int(target_height * img_ratio)
            
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(target_width, target_height))
        
        self.canvas_label.configure(image=imgtk, text="")

if __name__ == "__main__":
    app = TrafficApp()
    app.mainloop()
