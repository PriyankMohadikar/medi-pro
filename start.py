import subprocess
import sys
import time
import os

def start_backend():
    print("[1/2] Starting FastAPI Backend...")
    if sys.platform == "win32":
        backend_process = subprocess.Popen(["python", "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"], cwd="backend", creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        backend_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"], cwd="backend")
    return backend_process

def start_frontend():
    print("[2/2] Starting React Frontend...")
    # Using shell=True for npm on Windows
    frontend_process = subprocess.Popen(["npm", "run", "dev"], shell=(sys.platform == "win32"))
    return frontend_process

if __name__ == "__main__":
    print("==================================================")
    print("MediPrice Pro - Startup Orchestrator")
    print("==================================================")
    
    backend_p = start_backend()
    frontend_p = start_frontend()
    
    print("==================================================")
    print("[OK] Application stack started successfully.")
    print("- FastAPI running on http://localhost:8000")
    print("- Frontend running on http://localhost:3000")
    print("Press Ctrl+C to stop all services.")
    print("==================================================")
    
    try:
        backend_p.wait()
        frontend_p.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend_p.terminate()
        frontend_p.terminate()
        sys.exit(0)
