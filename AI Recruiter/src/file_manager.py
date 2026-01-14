import os
import time
from datetime import datetime

UPLOAD_DIR = "data/uploads"

def save_uploaded_file(uploaded_file):
    """
    Saves an uploaded file to the local disk.
    Returns the absolute path of the saved file.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    try:
        # Create a unique filename to prevent overwrites
        timestamp = int(time.time())
        clean_name = os.path.basename(uploaded_file.name)
        new_filename = f"{timestamp}_{clean_name}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return os.path.abspath(file_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return None
