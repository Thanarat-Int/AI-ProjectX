# 🐳 Docker Deployment Guide & Tutorial

This guide will help you containerize the **AI Resume Screener** and deploy it to a server. It's also a great way to learn Docker basics!

---

## 🏗️ 1. Understanding the Files (Structure)

We added 3 important files to your project:

1.  **`Dockerfile`**: The "Blueprint" for your container.
    *   It tells Docker: "Start with Python 3.10, install these libraries from requirements.txt, copy my code, and run `streamlit`."
2.  **`docker-compose.yml`**: The "Manager".
    *   It defines how to run the container. It maps ports (`8501`), connects volumes (to save data), and loads your `.env` key.
3.  **`.dockerignore`**: The "Gatekeeper".
    *   It tells Docker *what not to copy* into the image (like temporary files or your local `.env` which might contain secrets we don't want baked into the image layer).

---

## 🚀 2. How to Run (Local or Server)

### Prerequisites:
You need **Docker Desktop** installed on your machine (or Docker Engine on a Linux server).

### Steps:

#### Step A: Build & Start (The Magic Command)
Open your terminal in the project folder and run:
```bash
docker-compose up --build -d
```
*   `up`: Create and start containers.
*   `--build`: Force building the image (good for first time or after code changes).
*   `-d`: Detached mode (runs in background so it doesn't block your terminal).

#### Step B: Check Status
To see if it's running:
```bash
docker-compose ps
```

#### Step C: Access the App
Open your browser: `http://localhost:8501`

#### Step D: Stop it
When done, you can stop it with:
```bash
docker-compose down
```

---

## ☁️ 3. Deploying to a Server (e.g., DigitalOcean, AWS)

1.  **Get a Server**: A standard Ubuntu VPS (2GB RAM+) is sufficient.
2.  **Install Docker**: Follow official guides to install Docker & Docker Compose on the server.
3.  **Upload Project**: Copy your project folder to the server (you can use Git clone).
4.  **Add .env**: Make sure your `.env` file with the API KEY is on the server.
5.  **Run**: Execute `docker-compose up --build -d` on the server.
6.  **Done!**: Your app is live at `http://your-server-ip:8501`.

---

## 🎓 4. Docker Cheat Sheet
*   `docker ps`: List running containers.
*   `docker logs -f ai_resume_screener`: View live logs (useful for debugging).
*   `docker exec -it ai_resume_screener bash`: Go inside the container's shell.
