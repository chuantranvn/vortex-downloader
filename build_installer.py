import os
import sys
import subprocess
import shutil
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def print_banner(msg):
    print("\n" + "=" * 65)
    print(f"  {msg}")
    print("=" * 65 + "\n")

def ensure_ico_exists():
    ico_path = os.path.join(BASE_DIR, "client", "desktop_gui", "assets", "vortex_icon.ico")
    png_path = os.path.join(BASE_DIR, "client", "desktop_gui", "assets", "vortex_icon.png")
    if not os.path.exists(ico_path) and os.path.exists(png_path):
        print(" [*] Dang tao vortex_icon.ico tu file PNG...")
        from PIL import Image
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print(" [✓] Da tao vortex_icon.ico!")
    else:
        print(" [✓] File vortex_icon.ico da ton tai san.")

def find_iscc_compiler():
    candidates = [
        r"C:\Users\Lifetech\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    
    path_iscc = shutil.which("ISCC")
    if path_iscc:
        return path_iscc
    return None

def kill_running_instances():
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'VortexDownloader' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"],
                capture_output=True
            )
            time.sleep(0.5)
        except Exception:
            pass

def main():
    start_time = time.time()
    print_banner("⚡ VORTEX DOWNLOADER - BUILD SYSTEM & INSTALLER CREATOR")

    kill_running_instances()

    # 1. Đảm bảo Icon chuẩn Windows
    ensure_ico_exists()

    # 2. Chạy PyInstaller
    print_banner("BƯỚC 1: BIÊN DỊCH ỨNG DỤNG BẰNG PYINSTALLER")
    spec_path = os.path.join(BASE_DIR, "vortex.spec")
    pyinstaller_cmd = [sys.executable, "-m", "PyInstaller", spec_path, "--noconfirm"]
    
    print(f" [*] Dang chay: {' '.join(pyinstaller_cmd)}")
    res = subprocess.run(pyinstaller_cmd, cwd=BASE_DIR)
    if res.returncode != 0:
        print(" [!] LỖI: PyInstaller biên dịch thất bại!")
        sys.exit(1)
    print(" [✓] PyInstaller hoan tat thanh cong!")

    # 3. Chạy Inno Setup Compiler
    print_banner("BƯỚC 2: ĐÓNG GÓI BỘ CÀI ĐẶT WINDOWS BẰNG INNO SETUP")
    iscc_path = find_iscc_compiler()
    if not iscc_path:
        print(" [!] Khong tim thay trinh bien dich Inno Setup (ISCC.exe).")
        print("     Vui long cai dat Inno Setup 6.")
        sys.exit(1)

    print(f" [✓] Tim thay Inno Setup Compiler tai: {iscc_path}")
    installer_file = os.path.join(BASE_DIR, "installer_output", "Vortex_Downloader_Setup.exe")
    if os.path.exists(installer_file):
        try:
            os.remove(installer_file)
        except Exception:
            pass
    iss_script = os.path.join(BASE_DIR, "installer", "vortex_setup.iss")
    iscc_cmd = [iscc_path, iss_script]
    print(f" [*] Dang chay: {' '.join(iscc_cmd)}")
    res_inno = subprocess.run(iscc_cmd, cwd=BASE_DIR)
    if res_inno.returncode != 0:
        print(" [!] LỖI: Inno Setup biên dịch thất bại!")
        sys.exit(1)

    # 4. Báo cáo kết quả
    installer_file = os.path.join(BASE_DIR, "installer_output", "Vortex_Downloader_Setup.exe")
    elapsed = time.time() - start_time
    print_banner("🎉 HOÀN THÀNH ĐÓNG GÓI BỘ CÀI ĐẶT THÀNH CÔNG!")
    if os.path.exists(installer_file):
        size_mb = os.path.getsize(installer_file) / (1024 * 1024)
        print(f" [✓] File cài đặt: {installer_file}")
        print(f" [✓] Dung lượng  : {size_mb:.2f} MB")
        print(f" [✓] Thời gian   : {elapsed:.1f} giây")
        print("\n [★] Bạn có thể chạy trực tiếp file trên để cài đặt Vortex Downloader lên PC!")
    else:
        print(f" [!] Không tìm thấy file đầu ra tại: {installer_file}")

if __name__ == "__main__":
    main()
