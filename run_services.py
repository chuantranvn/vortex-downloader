import sys
import os
import subprocess
import time

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
PYTHON_EXE = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

def start_services():
    print("=" * 65)
    print("  🚀 KHOI DONG HE THONG MICROSERVICES - VORTEX DOWNLOADER (IDM)")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # 1. Khởi chạy Core Engine (Port 8001)
    print(" [1/3] Dang khoi dong Core Download Engine (Port 8001)...")
    core_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "services.core_engine.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=base_dir
    )

    # 2. Khởi chạy Media Extractor (Port 8002)
    print(" [2/3] Dang khoi dong Media Extractor Service (Port 8002)...")
    media_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "services.media_extractor.main:app", "--host", "127.0.0.1", "--port", "8002"],
        cwd=base_dir
    )

    time.sleep(1.5)

    # 3. Khởi chạy API Gateway (Port 8000)
    print(" [3/3] Dang khoi dong API Gateway & WebSocket Hub (Port 8000)...")
    gw_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "services.gateway.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=base_dir
    )

    print("\n" + "-" * 65)
    print(" [✓] TAT CA MICROSERVICES DA SAN SANG!")
    print("  -> API Gateway:         http://localhost:8000")
    print("  -> Swagger UI (Docs):   http://localhost:8000/docs")
    print("  -> Core Engine API:     http://localhost:8001/docs")
    print("  -> Media Extractor API: http://localhost:8002/docs")
    print("  -> WebSocket Realtime:  ws://localhost:8000/ws/progress")
    print("-" * 65)
    print(" Nhan Ctrl + C de dung toan bo he thong services.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n [!] Dang dung cac microservices...")
        for p in [gw_proc, media_proc, core_proc]:
            try:
                p.terminate()
            except Exception:
                pass
        print(" [✓] Da tat an toan toan bo services.")

if __name__ == "__main__":
    start_services()
