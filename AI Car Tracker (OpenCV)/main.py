import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
# 'yolov8n.pt' is the nano version (fastest, less accurate)
# It will automatically download on the first run.
model = YOLO('yolov8n.pt')

# Open the video file
video_path = "assets/car.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video file {video_path}")
    exit()

# Loop through the video frames
while cap.isOpened():
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        # stream=True is efficient for video loops (generators)
        results = model(frame, stream=True)

        # Visualize the results on the frame
        # results is a generator, so we iterate or pick the first one since we passed one frame
        for result in results:
            annotated_frame = result.plot()
            
            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
