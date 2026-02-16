import subprocess
import time
import os
import signal
import sys

def run_services():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")

    print("Starting services...")

    # Start Backend
    print("Starting Backend (FastAPI)...")
    uvicorn_path = os.path.join(base_dir, "backend", "venv", "Scripts", "uvicorn.exe")
    backend_process = subprocess.Popen(
        [uvicorn_path, "main:app", "--reload"],
        cwd=backend_dir,
        shell=True
    )


    # Start Frontend
    print("Starting Frontend (Vite)...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )

    print("\nServices are running!")
    print("   FastAPI Backend:  http://127.0.0.1:8000")
    print("   React+Vite Frontend: http://localhost:5173 (usually)")
    print("\nPress Ctrl+C to stop both services.\n")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        
        # Terminate processes
        backend_process.terminate()
        frontend_process.terminate()
        
        # Ensure they are killed on Windows
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("All services stopped.")

if __name__ == "__main__":
    run_services()
