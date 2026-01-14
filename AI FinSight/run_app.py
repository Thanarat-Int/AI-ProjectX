import subprocess
import time
import webbrowser
import os
import sys

def main():
    print("==========================================")
    print("       🚀 FinSight AI System Startup      ")
    print("==========================================")

    # 1. Start Backend (Uvicorn)
    print("[1/2] Starting Brain (Backend API)...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
    
    # Run in background
    backend_process = subprocess.Popen(backend_cmd, cwd=os.getcwd())
    
    # Wait simple health check (wait 3 seconds)
    print("      Waiting for neurons to fire...")
    time.sleep(3)
    
    # 2. Start Frontend (Streamlit)
    print("[2/2] Starting Interface (Dashboard)...")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "src/frontend/dashboard.py"]
    
    frontend_process = subprocess.Popen(frontend_cmd, cwd=os.getcwd())
    
    print("\n✅ System is Live!")
    print("   - API: http://localhost:8000/docs")
    print("   - UI:  http://localhost:8501")
    print("==========================================")
    print("PRESS CTRL+C TO SHUT DOWN")

    try:
        # Keep main script alive
        while True:
            time.sleep(1)
            # Check if processes are alive
            if backend_process.poll() is not None:
                print("⚠️ Backend died unexpectedly!")
                break
            if frontend_process.poll() is not None:
                print("⚠️ Frontend died unexpectedly!")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down system...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
