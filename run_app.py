import sys
import os
import subprocess
import time
import threading
import traceback

# Tự động chuyển sang môi trường ảo .venv nếu người dùng chạy bằng Python toàn cục
if not getattr(sys, "frozen", False):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_py = os.path.join(current_dir, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py) and os.path.normpath(sys.executable).lower() != os.path.normpath(venv_py).lower():
        result = subprocess.run([venv_py] + sys.argv, cwd=current_dir)
        sys.exit(result.returncode)

import httpx

def log_debug(msg: str):
    try:
        from common.database import get_app_data_dir
        log_file = os.path.join(get_app_data_dir(), "vortex.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %X')}] {msg}\n")
    except Exception:
        pass

class SafeStream:
    def write(self, s): pass
    def flush(self): pass
    def isatty(self): return False
    def reconfigure(self, **kwargs): pass

if sys.stdout is None:
    sys.stdout = SafeStream()
if sys.stderr is None:
    sys.stderr = SafeStream()

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

# Xác định BASE_DIR và đường dẫn ICON hoạt động cả khi chạy dev và khi đóng gói PyInstaller
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

# Đảm bảo BASE_DIR có trong sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Tìm kiếm icon
ICON_PATH = os.path.join(BASE_DIR, "client", "desktop_gui", "assets", "vortex_icon.png")
for cand in [
    os.path.join(BASE_DIR, "client", "desktop_gui", "assets", "vortex_icon.ico"),
    os.path.join(BASE_DIR, "client", "desktop_gui", "assets", "vortex_icon.png"),
    os.path.join(EXE_DIR, "vortex_icon.ico"),
    os.path.join(EXE_DIR, "client", "desktop_gui", "assets", "vortex_icon.ico"),
]:
    if os.path.exists(cand):
        ICON_PATH = cand
        break

def kill_existing_microservices():
    if sys.platform == "win32":
        try:
            cmd = "Get-NetTCPConnection -LocalPort 8000,8001,8002 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            time.sleep(0.5)
        except Exception:
            pass

def is_gateway_running() -> bool:
    try:
        r = httpx.get("http://localhost:8000/health", timeout=1.0)
        return r.status_code == 200
    except Exception:
        return False

def start_embedded_microservices():
    """Khởi chạy 3 vi dịch vụ FastAPI trên các daemon thread nội tại độc lập."""
    import uvicorn
    from services.core_engine.main import app as core_app
    from services.media_extractor.main import app as media_app
    from services.gateway.main import app as gateway_app

    def run_core():
        try:
            log_debug("Starting Core Engine on 127.0.0.1:8001...")
            config = uvicorn.Config(core_app, host="127.0.0.1", port=8001, log_level="warning", log_config=None)
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            log_debug(f"FATAL in Core Engine thread: {traceback.format_exc()}")

    def run_media():
        try:
            log_debug("Starting Media Extractor on 127.0.0.1:8002...")
            config = uvicorn.Config(media_app, host="127.0.0.1", port=8002, log_level="warning", log_config=None)
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            log_debug(f"FATAL in Media Extractor thread: {traceback.format_exc()}")

    def run_gateway():
        try:
            log_debug("Starting Gateway on 127.0.0.1:8000...")
            config = uvicorn.Config(gateway_app, host="127.0.0.1", port=8000, log_level="warning", log_config=None)
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            log_debug(f"FATAL in Gateway thread: {traceback.format_exc()}")

    threading.Thread(target=run_core, daemon=True, name="VortexCoreEngine").start()
    threading.Thread(target=run_media, daemon=True, name="VortexMediaExtractor").start()
    time.sleep(0.5)
    threading.Thread(target=run_gateway, daemon=True, name="VortexGateway").start()

def _main_inner():
    import multiprocessing
    multiprocessing.freeze_support()

    log_debug(f"Starting main_inner with argv={sys.argv}")
    print("=" * 65)
    print("  [VORTEX DOWNLOADER] KHOI DONG UNG DUNG DESKTOP")
    print("=" * 65)

    if "--restart" in sys.argv:
        print(" [*] Dang khoi dong lai cac Microservices...")
        kill_existing_microservices()

    if not is_gateway_running():
        print(" [*] Dang khoi dong cac Microservices noi bo...")
        log_debug("Starting embedded microservices...")
        start_embedded_microservices()

        for i in range(25):
            if is_gateway_running():
                log_debug(f"Microservices ready after {(i+1)*0.5}s")
                print(" [✓] Microservices da san sang!")
                break
            time.sleep(0.5)
        else:
            log_debug("WARNING: Gateway did not become ready within 12.5s")
    else:
        log_debug("Gateway already running on port 8000")
        print(" [✓] Phat hien Microservices dang hoat dong tai cong 8000.")

    print(" [*] Dang khoi tao giao dien Desktop GUI...")
    log_debug("Initializing PySide6 GUI...")
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon
    from PySide6.QtGui import QIcon, QColor, QPalette
    from client.desktop_gui.main_window import MainWindow
    from client.desktop_gui.styles import LIGHT_THEME_QSS

    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Vortex Downloader")

    pal = app.palette()
    pal.setColor(QPalette.Window, QColor("#f8fafc"))
    pal.setColor(QPalette.WindowText, QColor("#1e293b"))
    pal.setColor(QPalette.Base, QColor("#ffffff"))
    pal.setColor(QPalette.Text, QColor("#1e293b"))
    pal.setColor(QPalette.Button, QColor("#ffffff"))
    pal.setColor(QPalette.ButtonText, QColor("#1e293b"))
    app.setPalette(pal)

    app.setStyleSheet(LIGHT_THEME_QSS)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    window = MainWindow()

    # Kiểm tra cờ khởi động thu nhỏ (Auto-start cùng Windows)
    is_minimized = "--minimized" in sys.argv or "-m" in sys.argv
    if is_minimized:
        log_debug("App running in minimized mode")
        print(" [*] Khoi dong o che do chay ngam (System Tray)...")
        if hasattr(window, "tray") and window.tray.isVisible():
            window.tray.showMessage(
                "Vortex Downloader",
                "Ứng dụng đã khởi động ngầm cùng Windows và sẵn sàng hoạt động.",
                QSystemTrayIcon.Information,
                3000
            )
    else:
        log_debug("Showing main window")
        window.show()

    log_debug("Entering Qt event loop...")
    app.exec()
    log_debug("Qt event loop exited.")

def main():
    try:
        _main_inner()
    except Exception as e:
        log_debug(f"FATAL ERROR in main: {traceback.format_exc()}")
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            a = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "Vortex Downloader Error", f"Lỗi khởi động:\n{traceback.format_exc()}")
        except Exception:
            pass

if __name__ == "__main__":
    main()


