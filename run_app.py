import sys
import os
import time
import subprocess
import httpx

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    # Đăng ký AppUserModelID để Windows Taskbar hiển thị icon riêng của app thay vì icon Python
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("adjim.vortex.downloader.1.0")
    except Exception:
        pass

PYTHON_EXE = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "client", "desktop_gui", "assets", "vortex_icon.png")

def is_gateway_running() -> bool:
    try:
        r = httpx.get("http://localhost:8000/health", timeout=1.0)
        return r.status_code == 200
    except Exception:
        return False

def main():
    print("=" * 65)
    print("  [VORTEX DOWNLOADER] KHOI DONG UNG DUNG DESKTOP")
    print("=" * 65)

    services_procs = []
    if not is_gateway_running():
        print(" [*] Dang tu dong khoi dong cac Microservices phia sau...")
        
        core_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "services.core_engine.main:app", "--host", "127.0.0.1", "--port", "8001"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        services_procs.append(core_proc)

        media_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "services.media_extractor.main:app", "--host", "127.0.0.1", "--port", "8002"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        services_procs.append(media_proc)

        time.sleep(1.5)

        gw_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "services.gateway.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        services_procs.append(gw_proc)

        for _ in range(15):
            if is_gateway_running():
                print(" [✓] Microservices da san sang!")
                break
            time.sleep(0.5)
    else:
        print(" [✓] Phat hien Microservices dang hoat dong tai cong 8000.")

    print(" [*] Dang mo cua so Desktop GUI voi icon cao cap...")
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from client.desktop_gui.main_window import MainWindow

        app = QApplication.instance() or QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName("Vortex Downloader")
        if os.path.exists(ICON_PATH):
            app.setWindowIcon(QIcon(ICON_PATH))

        window = MainWindow()
        window.show()
        app.exec()
    finally:
        if services_procs:
            print("\n [*] Dang tat cac microservices chay ngam...")
            for p in services_procs:
                try:
                    p.terminate()
                except Exception:
                    pass
            print(" [✓] Da thoat hoan tat.")

if __name__ == "__main__":
    main()
