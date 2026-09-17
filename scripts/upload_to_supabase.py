#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vortex Downloader - Supabase Storage Release Uploader
Tự động tải file cài đặt Desktop (.exe) lên Supabase Storage và tạo Public Download URL.
Có khả năng chạy độc lập trên máy cục bộ hoặc trong quy trình GitHub Actions CI/CD.
"""

import os
import sys
import argparse
import time
import re
from pathlib import Path
from typing import Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import httpx
except ImportError:
    print(" [!] Thư viện 'httpx' chưa được cài đặt. Đang cài đặt httpx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx


def print_banner(msg: str):
    print("\n" + "=" * 65)
    print(f"  {msg}")
    print("=" * 65 + "\n")


class ProgressFileReader:
    """Đọc file theo luồng (streaming generator) để upload và báo cáo tiến trình."""
    def __init__(self, file_path: str, chunk_size: int = 4 * 1024 * 1024):
        self.file_path = file_path
        self.total_size = os.path.getsize(file_path)
        self.chunk_size = chunk_size
        self.uploaded_bytes = 0
        self.last_report_time = time.time()
        self.start_time = time.time()

    def __iter__(self):
        with open(self.file_path, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                self.uploaded_bytes += len(chunk)
                now = time.time()
                # Báo cáo tiến trình định kỳ hoặc khi hoàn tất
                if now - self.last_report_time >= 1.5 or self.uploaded_bytes == self.total_size:
                    percent = (self.uploaded_bytes / self.total_size) * 100
                    mb_done = self.uploaded_bytes / (1024 * 1024)
                    mb_total = self.total_size / (1024 * 1024)
                    elapsed = max(now - self.start_time, 0.001)
                    speed = mb_done / elapsed
                    print(f" [*] Đang tải lên: {mb_done:.1f} / {mb_total:.1f} MB ({percent:.1f}%) - Tốc độ: {speed:.2f} MB/s", end="\r")
                    self.last_report_time = now
                yield chunk
        print()  # Xuống dòng sau khi hoàn tất progress bar


def normalize_supabase_url(url: str) -> str:
    """Chuẩn hóa URL Supabase (loại bỏ dấu gạch chéo cuối)."""
    return url.strip().rstrip("/")


def ensure_bucket_exists(client: httpx.Client, base_url: str, headers: dict, bucket_name: str) -> bool:
    """Kiểm tra và tạo mới bucket nếu chưa có trên Supabase Storage."""
    bucket_url = f"{base_url}/storage/v1/bucket/{bucket_name}"
    try:
        r = client.get(bucket_url, headers=headers)
        if r.status_code == 200:
            print(f" [✓] Đã tìm thấy bucket '{bucket_name}' trên Supabase.")
            return True
        elif r.status_code == 404:
            print(f" [*] Bucket '{bucket_name}' chưa tồn tại. Đang tự động tạo bucket dạng PUBLIC...")
            create_url = f"{base_url}/storage/v1/bucket"
            create_payload = {
                "id": bucket_name,
                "name": bucket_name,
                "public": True,
                "file_size_limit": None,
                "allowed_mime_types": None
            }
            res = client.post(create_url, headers=headers, json=create_payload)
            if res.status_code in [200, 201]:
                print(f" [✓] Đã tạo thành công bucket PUBLIC: '{bucket_name}'!")
                return True
            else:
                print(f" [!] Cảnh báo: Không thể tự động tạo bucket ({res.status_code}): {res.text}")
                print("     Vui lòng đảm bảo bucket đã được tạo thủ công trên Supabase Dashboard.")
                return False
        else:
            print(f" [*] Kiểm tra bucket trả về status {r.status_code} (có thể do quyền của Key). Tiếp tục thử upload...")
            return True
    except Exception as e:
        print(f" [!] Lỗi khi kiểm tra bucket: {e}")
        return False


def upload_file_to_supabase(
    file_path: str,
    supabase_url: str,
    supabase_key: str,
    bucket_name: str,
    dest_path: str
) -> Tuple[bool, str]:
    """Upload 1 file nhị phân lên Supabase Storage qua REST API với x-upsert: true."""
    base_url = normalize_supabase_url(supabase_url)
    dest_path_clean = dest_path.strip().lstrip("/")
    upload_url = f"{base_url}/storage/v1/object/{bucket_name}/{dest_path_clean}"
    public_url = f"{base_url}/storage/v1/object/public/{bucket_name}/{dest_path_clean}"

    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
        "x-upsert": "true",
        "Content-Type": "application/octet-stream",
    }

    print(f"\n [+] Bắt đầu upload: {os.path.basename(file_path)}")
    print(f"     Đích đến: bucket '{bucket_name}' -> /{dest_path_clean}")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"     Kích thước file: {file_size_mb:.2f} MB")

    # Timeout cấu hình lớn cho file dung lượng > 100MB
    timeout_config = httpx.Timeout(connect=60.0, read=300.0, write=300.0, pool=60.0)

    with httpx.Client(timeout=timeout_config) as client:
        # Kiểm tra bucket
        ensure_bucket_exists(client, base_url, headers, bucket_name)

        reader = ProgressFileReader(file_path)
        try:
            res = client.post(upload_url, headers=headers, content=reader)
            if res.status_code in [200, 201]:
                print(f" [✓] Upload hoàn tất thành công (Status {res.status_code})!")
                print(f" [★] Link tải Public: {public_url}")
                return True, public_url
            else:
                print(f" [!] LỖI upload (Status {res.status_code}): {res.text}")
                if res.status_code == 413:
                    print(" [!] GỢI Ý KHẮC PHỤC: Lỗi 'Payload Too Large' (413).")
                    print("     File của bạn vượt quá giới hạn file size limit của Supabase.")
                    print("     Vui lòng vào Supabase Dashboard -> Storage -> Buckets -> Edit Bucket -> Tăng 'Max file size' (hoặc nâng lên 500MB).")
                elif res.status_code in [401, 403]:
                    print(" [!] GỢI Ý KHẮC PHỤC: Lỗi 'Unauthorized' / 'Permission Denied'.")
                    print("     Vui lòng kiểm tra lại SUPABASE_KEY. Hãy sử dụng 'service_role' secret key để có toàn quyền ghi vào Storage.")
                return False, ""
        except Exception as e:
            print(f" [!] Ngoại lệ xảy ra khi upload: {e}")
            return False, ""


def write_github_summary(results: list, file_size_mb: float):
    """Ghi bảng thông tin tóm tắt vào GITHUB_STEP_SUMMARY để hiển thị trên web GitHub Actions."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    try:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write("\n## 🚀 Vortex Downloader - Release Artifacts (Supabase Storage)\n\n")
            f.write(f"- **Dung lượng file cài đặt:** `{file_size_mb:.2f} MB`\n")
            f.write("- **Nền tảng hỗ trợ:** Windows 10/11 (64-bit)\n\n")
            f.write("| Tên file | Điểm đích (Path) | Đường dẫn tải trực tiếp (Public Download URL) |\n")
            f.write("| :--- | :--- | :--- |\n")
            for item in results:
                name = item.get("name", "")
                path = item.get("path", "")
                url = item.get("url", "")
                f.write(f"| **{name}** | `{path}` | [📥 Tải ngay ({name})]({url}) |\n")
            f.write("\n> ✨ *File đã được upload tự động lên Supabase Storage với cờ `x-upsert: true`.*\n\n")
    except Exception as e:
        print(f" [!] Không thể ghi GITHUB_STEP_SUMMARY: {e}")


def write_github_outputs(latest_url: str, version_url: str):
    """Ghi output vào GITHUB_OUTPUT để các step sau trong workflow có thể sử dụng."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return

    try:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"latest_url={latest_url}\n")
            f.write(f"version_url={version_url}\n")
    except Exception as e:
        print(f" [!] Không thể ghi GITHUB_OUTPUT: {e}")


def main():
    parser = argparse.ArgumentParser(description="Upload Vortex Downloader Installer to Supabase Storage")
    parser.add_argument("--file", type=str, default=None, help="Đường dẫn đến file cài đặt .exe")
    parser.add_argument("--url", type=str, default=None, help="Supabase Project URL (hoặc qua biến SUPABASE_URL)")
    parser.add_argument("--key", type=str, default=None, help="Supabase Service Role Key (hoặc qua biến SUPABASE_KEY)")
    parser.add_argument("--bucket", type=str, default=None, help="Tên bucket Supabase Storage (mặc định: releases)")
    parser.add_argument("--version", type=str, default=None, help="Phiên bản phát hành (ví dụ: 1.0.0 hoặc v1.0.0)")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử nghiệm kiểm tra không gửi request thực tế")
    parser.add_argument("--skip-on-missing-creds", action="store_true", help="Bỏ qua không báo lỗi nếu thiếu SUPABASE credentials")

    args = parser.parse_args()

    print_banner("⚡ VORTEX DOWNLOADER - SUPABASE STORAGE UPLOADER")

    # 1. Xác định file cần upload
    root_dir = Path(__file__).resolve().parent.parent
    file_path = args.file
    if not file_path:
        default_installer = root_dir / "installer_output" / "Vortex_Downloader_Setup.exe"
        if default_installer.exists():
            file_path = str(default_installer)
        else:
            print(f" [!] Không tìm thấy file mặc định tại: {default_installer}")
            print("     Vui lòng truyền đường dẫn file qua tham số --file <đường_dẫn>")
            sys.exit(1)

    if not os.path.exists(file_path):
        print(f" [!] File không tồn tại: {file_path}")
        sys.exit(1)

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    file_name = os.path.basename(file_path)
    print(f" [✓] File nguồn  : {file_path}")
    print(f" [✓] Tên file    : {file_name}")
    print(f" [✓] Kích thước  : {file_size_mb:.2f} MB")

    # 2. Lấy thông tin xác thực Supabase
    supabase_url = args.url or os.environ.get("SUPABASE_URL")
    supabase_key = args.key or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    bucket_name = args.bucket or os.environ.get("SUPABASE_BUCKET", "releases")

    # 3. Xác định phiên bản (Version)
    version = args.version or os.environ.get("VERSION") or os.environ.get("GITHUB_REF_NAME") or "1.0.0"
    # Chuẩn hóa version (bỏ chữ v đầu nếu có để thống nhất)
    version_clean = re.sub(r"^v", "", version).strip()

    print(f" [✓] Phiên bản   : {version_clean}")
    print(f" [✓] Bucket đích : {bucket_name}")

    if not supabase_url or not supabase_key:
        print("\n" + "!" * 65)
        print(" [!] THIẾU THÔNG TIN XÁC THỰC SUPABASE:")
        print("     - SUPABASE_URL chưa được thiết lập.")
        print("     - SUPABASE_KEY / SUPABASE_SERVICE_ROLE_KEY chưa được thiết lập.")
        print("\n [★] HƯỚNG DẪN CẤU HÌNH GITHUB ACTIONS SECRETS:")
        print("     1. Vào repository GitHub -> Settings -> Secrets and variables -> Actions")
        print("     2. Nhấn 'New repository secret'")
        print("     3. Thêm secret: SUPABASE_URL (ví dụ: https://xyz.supabase.co)")
        print("     4. Thêm secret: SUPABASE_KEY (Lấy 'service_role' key từ Project Settings -> API)")
        print("     5. Thêm secret: SUPABASE_BUCKET (tùy chọn, mặc định: releases)")
        print("!" * 65 + "\n")

        if args.skip_on_missing_creds or os.environ.get("SKIP_ON_MISSING_CREDS") == "true":
            print(" [*] Đã bật chế độ 'skip-on-missing-creds'. Bỏ qua bước upload Supabase một cách an toàn.")
            sys.exit(0)
        else:
            sys.exit(1)

    if args.dry_run:
        print(" [*] Đang chạy ở chế độ DRY-RUN (không upload thực tế).")
        print(f" [✓] Giả lập URL: {supabase_url}/storage/v1/object/public/{bucket_name}/latest/{file_name}")
        sys.exit(0)

    # 4. Thực hiện upload lên 2 vị trí:
    #    a) latest/Vortex_Downloader_Setup.exe (Link tải bản mới nhất cố định)
    #    b) releases/v{version}/Vortex_Downloader_Setup.exe (Lưu trữ theo từng bản phát hành)
    destinations = [
        f"latest/{file_name}",
        f"releases/v{version_clean}/{file_name}",
    ]

    successful_uploads = []
    latest_url = ""
    version_url = ""

    for dest in destinations:
        success, url = upload_file_to_supabase(
            file_path=file_path,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            bucket_name=bucket_name,
            dest_path=dest
        )
        if success:
            successful_uploads.append({
                "name": file_name,
                "path": dest,
                "url": url
            })
            if dest.startswith("latest/"):
                latest_url = url
            else:
                version_url = url

    if not successful_uploads:
        print("\n [!] Quá trình upload thất bại. Vui lòng kiểm tra lại cấu hình Supabase.")
        sys.exit(1)

    # 5. Báo cáo kết quả ra GitHub Actions
    write_github_summary(successful_uploads, file_size_mb)
    write_github_outputs(latest_url, version_url)

    print_banner("🎉 ĐÃ HOÀN TẤT UPLOAD TẤT CẢ FILE LÊN SUPABASE STORAGE!")
    for item in successful_uploads:
        print(f" [✓] {item['path']} -> {item['url']}")
    print()


if __name__ == "__main__":
    main()
