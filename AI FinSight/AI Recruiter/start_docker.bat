@echo off
echo ==============================================
echo 🐳 AI Resume Screener - Docker Launcher
echo ==============================================
echo.
echo [1/3] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running! 
    echo Please open 'Docker Desktop' and try again.
    pause
    exit /b
)

echo.
echo [2/3] Building and Starting Container...
echo (First time may take a few minutes to download Python...)
docker-compose up -d --build

echo.
echo [3/3] Done! App is running in background.
echo.
echo ----------------------------------------------
echo 🌐 Open Browser: http://localhost:8501
echo ----------------------------------------------
echo.
pause
