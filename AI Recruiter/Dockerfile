# 1. Base Image: Use lightweight Python 3.10
FROM python:3.10-slim

# 2. Set Working Directory
WORKDIR /app

# 3. Install System Dependencies (Required for PDF processing)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy Requirements & Install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
COPY . .

# 6. Expose Port (Streamlit default)
EXPOSE 8501

# 7. Define Volume for Data Persistence (Optional, handled in compose)
VOLUME ["/app/data"]

# 8. Command to Run
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
