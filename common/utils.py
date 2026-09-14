import os
import re
from typing import Optional, List, Set

def sanitize_filename(name: str) -> str:
    """Loại bỏ ký tự không hợp lệ trong tên file trên hệ điều hành Windows."""
    cleaned = "".join(c for c in name if c not in r'\/:*?"<>|').strip()
    return cleaned if cleaned else "download"

def clean_video_url(url: str) -> str:
    """Loại bỏ các tham số playlist, mix radio thừa (&list=..., &start_radio=...) để tránh quét cả danh sách gây timeout."""
    if not url:
        return url
    url = url.strip()
    if "youtube.com/watch" in url:
        m = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
        if m:
            return f"https://www.youtube.com/watch?v={m.group(1)}"
    elif "youtu.be/" in url:
        m = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if m:
            return f"https://www.youtube.com/watch?v={m.group(1)}"
    return url

def get_unique_filepath(directory: str, filename: str, reserved_paths: Optional[List[str]] = None) -> str:
    """
    Tìm đường dẫn file duy nhất chưa bị trùng trong thư mục `directory`.
    Nếu file đã tồn tại hoặc cùng base name với các định dạng media khác,
    hoặc đang có task khác sử dụng tên này, hàm sẽ tự động đánh số
    (1), (2), (3)... vào sau tên file.
    """
    base, ext = os.path.splitext(filename)
    base = sanitize_filename(base).strip()
    ext = ext.strip()

    counter = 0
    reserved: Set[str] = set(os.path.normpath(p).lower() for p in (reserved_paths or []))
    media_exts = {ext.lower(), ".mp4", ".mkv", ".webm", ".mp3", ".m4a", ".aac", ".part", ".ytdl", ".temp"}

    while True:
        candidate_base = base if counter == 0 else f"{base} ({counter})"
        candidate_name = f"{candidate_base}{ext}"
        candidate_path = os.path.join(directory, candidate_name)
        norm_path = os.path.normpath(candidate_path).lower()

        # 1. Trùng với task đang chạy
        if norm_path in reserved:
            counter += 1
            continue

        # 2. File đã tồn tại trên đĩa
        if os.path.exists(candidate_path):
            counter += 1
            continue

        # 3. Trùng với file media khác cùng tên trên đĩa (kể cả .part, .webm, .mkv...)
        has_duplicate = False
        try:
            if os.path.exists(directory):
                for f in os.listdir(directory):
                    f_base, f_ext = os.path.splitext(f)
                    if f_base.lower() == candidate_base.lower():
                        if f_ext.lower() in media_exts or not f_ext:
                            has_duplicate = True
                            break
        except Exception:
            pass

        if has_duplicate:
            counter += 1
            continue

        return candidate_path
