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

def get_default_download_dir() -> str:
    """
    Trả về thư mục tải mặc định:
    - Khi chạy đóng gói (.exe): %USERPROFILE%/Downloads/Vortex Downloads
    - Khi dev: thư mục downloads trong codebase
    """
    import sys
    if getattr(sys, "frozen", False):
        user_dl = os.path.join(os.path.expanduser("~"), "Downloads", "Vortex Downloads")
        os.makedirs(user_dl, exist_ok=True)
        return user_dl
    else:
        dev_dl = os.path.abspath(os.path.join(os.path.dirname(__file__), "../downloads"))
        os.makedirs(dev_dl, exist_ok=True)
        return dev_dl

def is_autostart_enabled() -> bool:
    """Kiểm tra xem Vortex Downloader có được cấu hình khởi động cùng Windows không."""
    import sys
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "VortexDownloader")
            return bool(val)
    except Exception:
        return False

def set_autostart(enable: bool) -> bool:
    """Bật hoặc tắt tính năng khởi động cùng Windows trong HKCU Run Registry."""
    import sys
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                exe_path = sys.executable
                cmd = f'"{exe_path}" --minimized'
                winreg.SetValueEx(key, "VortexDownloader", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, "VortexDownloader")
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"[Autostart] Error updating registry: {e}")
        return False

def parse_error_details(err_raw: str, url: str = "") -> dict:
    """
    Phân tích chuỗi lỗi từ backend/yt-dlp và trả về thông tin chi tiết:
    - summary: Tóm tắt nguyên nhân lỗi dễ hiểu
    - suggestion: Hướng dẫn người dùng cách khắc phục
    - technical_detail: Chi tiết kỹ thuật đầy đủ
    """
    import json
    detail = str(err_raw or "")
    try:
        j = json.loads(err_raw)
        if isinstance(j, dict) and "detail" in j:
            detail = str(j["detail"])
    except Exception:
        pass

    lower = detail.lower() + " " + (url or "").lower()

    # 1. Unsupported URL
    if "unsupported url" in lower:
        if "facebook.com" in lower:
            summary = "Đường dẫn Facebook không phải video trực tiếp (là link trang chủ hoặc Bảng tin)."
            suggestion = (
                "• Với Facebook: Hãy mở hẳn trang xem video riêng biệt (Watch, Reels hoặc bài viết chi tiết) thay vì dùng link Bảng tin (facebook.com).\n"
                "• Bạn có thể bấm nút 'Chia sẻ' trên bài viết Facebook -> chọn 'Sao chép liên kết' để lấy đúng link video."
            )
        elif any(web in lower for web in ["motchill", "rophim", "phim", "anime", "stream"]):
            summary = "Trang web xem phim sử dụng trình phát nhúng bảo vệ (không có file video trực tiếp trên URL trang)."
            suggestion = (
                "• Các trang web xem phim thường truyền video qua luồng trực tuyến HLS (.m3u8).\n"
                "• Vui lòng lấy link luồng trực tiếp (.m3u8 hoặc .mp4) để dán vào đây tải đa luồng tốc độ cao."
            )
        else:
            summary = "Đường dẫn URL này không được hỗ trợ bóc tách trực tiếp."
            suggestion = (
                "• Đảm bảo liên kết dẫn trực tiếp tới trang video (YouTube, TikTok, Facebook Reel/Watch) hoặc tệp tin media trực tiếp (.mp4, .m3u8, .zip, .iso...).\n"
                "• Kiểm tra xem đường dẫn có bị sai chính tả hoặc thiếu ký tự không."
            )
    # 2. Login required / redirect to login.php
    elif "login.php" in lower or ("sign in" in lower and "bot" not in lower):
        summary = "Nội dung này yêu cầu đăng nhập tài khoản hoặc bị giới hạn quyền riêng tư."
        suggestion = (
            "• Trang web chuyển hướng đến trang đăng nhập (Facebook / Website có bảo mật).\n"
            "• Hãy đảm bảo video ở chế độ Công khai (Public) hoặc đồng bộ Cookies tài khoản trước khi tải."
        )
    # 3. YouTube bot detection
    elif "confirm you're not a bot" in lower or "bot" in lower:
        summary = "YouTube kích hoạt cơ chế chống tự động (Bot Detection)."
        suggestion = (
            "• Mở video trên trình duyệt Chrome và bấm nút tải từ Tiện ích mở rộng Vortex Extension để tự động gửi Cookie xác minh danh tính."
        )
    # 4. Connection / Gateway error
    elif "connect" in lower or "gateway" in lower or "timeout" in lower:
        summary = "Không thể kết nối đến dịch vụ phân tích nội bộ (Gateway / Media Extractor)."
        suggestion = (
            "• Đảm bảo ứng dụng Vortex và các microservices đang chạy bình thường.\n"
            "• Kiểm tra kết nối mạng Internet của máy tính."
        )
    else:
        summary = "Không thể trích xuất thông tin video từ đường dẫn này."
        suggestion = (
            "• Kiểm tra lại xem video có đang phát bình thường trên trình duyệt không.\n"
            "• Nếu là file tải trực tiếp hoặc luồng stream, bạn vẫn có thể bấm 'Bắt đầu tải ngay' để thử tải."
        )

    return {
        "summary": summary,
        "suggestion": suggestion,
        "technical_detail": detail
    }


