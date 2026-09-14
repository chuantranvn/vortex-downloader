import sys
import os
import subprocess
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def stop_all_services():
    print("=" * 65)
    print("  🛑 DỪNG TOÀN BỘ TIẾN TRÌNH MICROSERVICES - VORTEX DOWNLOADER")
    print("=" * 65)

    ports = [8000, 8001, 8002]
    killed_pids = set()

    if sys.platform == "win32":
        try:
            cmd = "Get-NetTCPConnection -LocalPort 8000,8001,8002 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
            pids = [line.strip() for line in res.stdout.strip().splitlines() if line.strip().isdigit()]

            for pid in pids:
                pid_int = int(pid)
                if pid_int == 0 or pid_int == os.getpid():
                    continue
                try:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid_int)], capture_output=True)
                    killed_pids.add(pid_int)
                    print(f" [✓] Đã giải phóng tiến trình PID: {pid_int}")
                except Exception:
                    pass
        except Exception as e:
            print(f" [!] Lỗi khi quét cổng: {e}")
    else:
        for port in ports:
            try:
                out = subprocess.check_output(["lsof", "-ti", f":{port}"]).decode().strip()
                for pid in out.splitlines():
                    if pid.isdigit():
                        subprocess.run(["kill", "-9", pid])
                        killed_pids.add(int(pid))
                        print(f" [✓] Đã giải phóng tiến trình PID: {pid} (Port {port})")
            except Exception:
                pass

    time.sleep(0.5)
    if killed_pids:
        print(f"\n [✓] Đã tắt thành công {len(killed_pids)} tiến trình chạy ngầm (Cổng 8000, 8001, 8002).")
    else:
        print(" [i] Không có tiến trình microservice nào đang chạy trên các cổng 8000, 8001, 8002.")
    print("=" * 65)

if __name__ == "__main__":
    stop_all_services()
