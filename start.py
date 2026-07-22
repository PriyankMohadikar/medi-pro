import subprocess
import sys
import time
import urllib.request
import os
import json

def check_ollama_running():
    try:
        req = urllib.request.Request("http://localhost:11434/")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def check_model_available(model_name="qwen2.5:7b"):
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            models = [m.get("name") for m in data.get("models", [])]
            return any(model_name in name for name in models)
    except Exception:
        return False

def start_ollama():
    print("[1/4] Checking Ollama...")
    if check_ollama_running():
        print("[OK] Ollama is already running.")
    else:
        print("[WARN] Ollama is not running. Attempting to start 'ollama serve' in background...")
        # Start ollama serve in background
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["ollama", "serve"], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for it to start
        for _ in range(10):
            time.sleep(1)
            if check_ollama_running():
                print("[OK] Ollama started successfully.")
                break
        else:
            print("[ERROR] Failed to start Ollama automatically. Please start it manually.")
            sys.exit(1)

def verify_model(model_name="qwen2.5:7b"):
    print(f"[2/4] Verifying model {model_name}...")
    if check_model_available(model_name):
        print(f"[OK] Model {model_name} is ready.")
    else:
        print(f"[WARN] Model {model_name} is missing. Attempting to pull... (This may take several minutes)")
        result = subprocess.run(["ollama", "pull", model_name])
        if result.returncode == 0:
            print(f"[OK] Model {model_name} downloaded successfully.")
        else:
            print(f"[ERROR] Failed to download model {model_name}. Please run 'ollama pull {model_name}' manually.")
            sys.exit(1)

def start_backend():
    print("[3/4] Starting FastAPI Backend...")
    if sys.platform == "win32":
        backend_process = subprocess.Popen(["python", "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"], cwd="backend", creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        backend_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"], cwd="backend")
    return backend_process

def start_frontend():
    print("[4/4] Starting React Frontend...")
    # Using shell=True for npm on Windows
    frontend_process = subprocess.Popen(["npm", "run", "dev"], shell=(sys.platform == "win32"))
    return frontend_process

if __name__ == "__main__":
    print("==================================================")
    print("MediPrice Pro - Startup Orchestrator")
    print("==================================================")
    
    start_ollama()
    
    # Check .env or default to qwen2.5:7b
    model = "qwen2.5:7b"
    if os.path.exists("backend/.env"):
        with open("backend/.env", "r") as f:
            for line in f:
                if line.startswith("OLLAMA_MODEL="):
                    model = line.strip().split("=", 1)[1]
    verify_model(model)
    
    backend_p = start_backend()
    frontend_p = start_frontend()
    
    print("==================================================")
    print("[OK] Application stack started successfully.")
    print("- FastAPI running on http://localhost:8000")
    print("- Frontend running on http://localhost:3000")
    print("- Ollama connected")
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
