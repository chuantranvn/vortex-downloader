import asyncio
import hashlib
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.core_engine.engine import HttpRangeDownloadEngine
from services.media_extractor.extractor import MediaExtractorEngine
from common.schemas import TaskStatus

TEST_DIR = os.path.abspath("test_workspace")
os.makedirs(TEST_DIR, exist_ok=True)
MOCK_FILE = os.path.join(TEST_DIR, "source_5mb.bin")

# Tạo file test 5MB ngẫu nhiên
FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes
test_data = os.urandom(FILE_SIZE)
with open(MOCK_FILE, "wb") as f:
    f.write(test_data)
source_hash = hashlib.sha256(test_data).hexdigest()

class RangeHttpServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(FILE_SIZE))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Disposition", 'attachment; filename="verified_file.bin"')
        self.end_headers()

    def do_GET(self):
        range_header = self.headers.get("Range")
        if range_header and range_header.startswith("bytes="):
            parts = range_header.replace("bytes=", "").split("-")
            start = int(parts[0])
            end = int(parts[1]) if parts[1] else FILE_SIZE - 1
            length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Range", f"bytes {start}-{end}/{FILE_SIZE}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            self.wfile.write(test_data[start:end+1])
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(FILE_SIZE))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            self.wfile.write(test_data)

    def log_message(self, format, *args):
        pass

async def run_tests():
    print("==========================================================")
    print("  [TEST] BAT DAU KIEM THU HE THONG VORTEX DOWNLOADER")
    print("==========================================================")

    # 1. Khởi chạy Mock Server
    server = HTTPServer(("127.0.0.1", 8899), RangeHttpServer)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(" [+] Mock HTTP Range Server da san sang tai port 8899.")

    # 2. Test Core Engine (Băm file 8 luồng + ghép file)
    print("\n [TEST 1] Kiem tra Loi tai da luong HTTP Range (8 luong)...")
    core_engine = HttpRangeDownloadEngine(default_download_dir=os.path.join(TEST_DIR, "downloads"))
    
    test_url = "http://127.0.0.1:8899/verified_file.bin"
    task = await core_engine.create_download_task(
        url=test_url,
        num_threads=8,
        file_name="result_downloaded.bin"
    )
    print(f"       -> Task ID: {task.id}")
    print(f"       -> So luong phan bo: {task.num_threads} chunks")
    print(f"       -> Dung luong file: {task.total_bytes / (1024*1024):.2f} MB")

    # Đợi tải xong
    while task.status in (TaskStatus.QUEUED, TaskStatus.DOWNLOADING, TaskStatus.MERGING):
        await asyncio.sleep(0.1)

    assert task.status == TaskStatus.COMPLETED, f"Task that bai: {task.error_message}"
    print(f" [+] Tai da luong hoan tat! Trang thai: {task.status}")

    # Kiểm tra tính toàn vẹn file sau ghép (Checksum)
    with open(task.save_path, "rb") as f:
        downloaded_hash = hashlib.sha256(f.read()).hexdigest()

    assert downloaded_hash == source_hash, "LOI: Hash file tai ve khong khop!"
    print(f" [+] SHA-256 Checksum khop 100%: {downloaded_hash[:20]}...")

    # 3. Test Media Extractor & Bundled FFmpeg
    print("\n [TEST 2] Kiem tra Media Extractor & Bundled FFmpeg...")
    media_engine = MediaExtractorEngine(default_download_dir=os.path.join(TEST_DIR, "media_dl"))
    assert os.path.exists(media_engine.ffmpeg_path), f"Khong tim thay FFmpeg: {media_engine.ffmpeg_path}"
    print(f" [+] FFmpeg nhung san da san sang tai: {media_engine.ffmpeg_path}")

    server.shutdown()
    print("\n==========================================================")
    print(" [SUCCESS] TAT CA CAC BAI KIEM THU DA PASS 100%!")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
