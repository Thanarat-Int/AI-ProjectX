import cv2
from ultralytics import YOLO
import numpy as np
import time
import csv
import math

class TrafficAnalyzer:
    def __init__(self, model_path='yolov8n.pt'):
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
        print("Model loaded successfully.")
        
        # --- Config ---
        # Line position (y-coordinate) - adjust based on video resolution (e.g., car.mp4)
        self.line_y = 350 
        self.offset = 10 # Tolerance for crossing line
        
        # Speed constants (Approximate for demo)
        self.ppm = 8 # Pixels per Meter (Calibration factor)
        
        # --- State ---
        self.counts = {"car": 0, "bus": 0, "truck": 0, "motorcycle": 0, "total": 0}
        self.counted_ids = set()
        self.previous_positions = {} # {id: (x, y, timestamp)}
        
        # Prepare CSV Log
        self.log_file = "traffic_log.csv"
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Vehicle ID", "Class", "Speed (km/h)"])

    def process_frame(self, frame):
        # 1. Run inference with Tracking
        # Filter classes: 2=car, 3=motorcycle, 5=bus, 7=truck
        # conf=0.5 prevents "Ghost IDs" (faint detections)
        results = self.model.track(frame, persist=True, verbose=False, classes=[2, 3, 5, 7], conf=0.5)
        
        height, width, _ = frame.shape
        # Dynamic line positioning (if not set manually, use 60% of height)
        if self.line_y == 0: self.line_y = int(height * 0.6)
            
        annotated_frame = frame.copy()
        
        # Draw Counting Line (DISABLED VALIDATION: User requested removal)
        # cv2.line(annotated_frame, (0, self.line_y), (width, self.line_y), (0, 255, 255), 2)
        # cv2.putText(annotated_frame, "Counting Line", (10, self.line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # 2. Process Detections
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            cls_indices = results[0].boxes.cls.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu().tolist()

            for box, track_id, cls_idx, conf in zip(boxes, track_ids, cls_indices, confidences):
                x1, y1, x2, y2 = map(int, box)
                w, h = x2 - x1, y2 - y1
                cx, cy = x1 + w // 2, y1 + h // 2
                
                class_name = self.model.names[cls_idx]
                
                # --- A. Crossing Logic ---
                if (self.line_y < cy < self.line_y + self.offset) or (self.line_y - self.offset < cy < self.line_y):
                    if track_id not in self.counted_ids:
                        self.counted_ids.add(track_id)
                        
                        # Increment specific class counter
                        if class_name in self.counts:
                            self.counts[class_name] += 1
                        else:
                            # Group unknown vehicles or other classes
                            self.counts.setdefault("other", 0)
                            self.counts["other"] += 1
                            
                        self.counts["total"] += 1
                        
                        # Visual effect (Line turns green temporarily - hard to do in single frame logic without state, skipping for simplicity)
                        cv2.circle(annotated_frame, (cx, cy), 10, (0, 255, 0), -1)

                # --- B. Speed Estimation ---
                speed_kmh = 0
                if track_id in self.previous_positions:
                    prev_x, prev_y, prev_time = self.previous_positions[track_id]
                    curr_time = time.time()
                    
                    # Calculate distance (pixels)
                    distance_pixels = math.sqrt((cx - prev_x)**2 + (cy - prev_y)**2)
                    
                    # Calculate speed
                    # Speed (m/s) = (Pixels / PPM) / Time_diff
                    time_diff = curr_time - prev_time
                    if time_diff > 0:
                        speed_ms = (distance_pixels / self.ppm) / time_diff
                        speed_kmh = speed_ms * 3.6
                
                # Update position for next frame
                self.previous_positions[track_id] = (cx, cy, time.time())

                # --- C. Visualization ---
                # Draw Box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw Info (ID, Class, Speed)
                label = f"ID:{track_id} {class_name} {int(speed_kmh)} km/h"
                cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                 # --- D. Logging (Once per crossing for simplicity, or periodically) ---
                # Here we log when it crosses the line
                if track_id in self.counted_ids and (self.line_y - self.offset < cy < self.line_y + self.offset):
                     # Write to CSV
                     with open(self.log_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), track_id, class_name, int(speed_kmh)])

        return annotated_frame

    def get_counts(self):
        """Return current counts dictionary."""
        return self.counts

    def reset(self):
        """Reset all counters and state."""
        self.counts = {"car": 0, "bus": 0, "truck": 0, "motorcycle": 0, "total": 0}
        self.counted_ids = set()
        self.previous_positions = {}
