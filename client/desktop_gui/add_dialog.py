import sys
import os
import re
from typing import Optional
import httpx
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPalette, QColor

from common.utils import clean_video_url, get_default_download_dir
from client.desktop_gui.loading_overlay import LoadingOverlay
from client.desktop_gui.styles import LIGHT_THEME_QSS

GATEWAY_URL = "http://localhost:8000"
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/vortex_icon.png"))

STANDARD_PRESETS = [
    ("🌟 Giữ nguyên định dạng & chất lượng gốc (Original Best)", "bestvideo+bestaudio/best"),
    ("🎬 4320p (8K UHD)", "bestvideo[height<=4320]+bestaudio/best"),
    ("🎬 2160p (4K UHD)", "bestvideo[height<=2160]+bestaudio/best"),
    ("🎬 1440p (2K QHD)", "bestvideo[height<=1440]+bestaudio/best"),
    ("🖥️ 1080p Full HD", "bestvideo[height<=1080]+bestaudio/best"),
    ("📺 720p HD", "bestvideo[height<=720]+bestaudio/best"),
    ("📱 480p SD", "bestvideo[height<=480]+bestaudio/best"),
    ("📱 360p", "bestvideo[height<=360]+bestaudio/best"),
    ("📱 240p", "bestvideo[height<=240]+bestaudio/best"),
    ("📱 180p", "bestvideo[height<=180]+bestaudio/best"),
    ("📱 144p", "bestvideo[height<=144]+bestaudio/best"),
    ("🎵 Chỉ tải Âm thanh (Audio MP3)", "audio_only"),
]

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()

def format_approx_size(num_bytes: int) -> str:
    if not num_bytes or num_bytes <= 0:
        return ""
    if num_bytes < 1024 * 1024:
        return f" (~{num_bytes / 1024:.1f} KB)"
    elif num_bytes < 1024 * 1024 * 1024:
        return f" (~{num_bytes / (1024 * 1024):.1f} MB)"
    else:
        return f" (~{num_bytes / (1024 * 1024 * 1024):.2f} GB)"

class AnalyzeWorker(QThread):
    success = Signal(dict)
    failed = Signal(str)

    def __init__(self, url: str, cookies: Optional[str]):
        super().__init__()
        self.url = url
        self.cookies = cookies

    def run(self):
        try:
            req_body = {"url": self.url}
            if self.cookies:
                req_body["cookies"] = self.cookies
            with httpx.Client(timeout=20.0) as client:
                res = client.post(f"{GATEWAY_URL}/api/v1/extract", json=req_body)
                if res.status_code == 200:
                    self.success.emit(res.json())
                else:
                    self.failed.emit(res.text)
        except Exception as e:
            self.failed.emit(str(e))

class DownloadStarterWorker(QThread):
    success = Signal(dict)
    failed = Signal(str)

    def __init__(self, payload: dict):
        super().__init__()
        self.payload = payload

    def run(self):
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{GATEWAY_URL}/api/v1/download", json=self.payload)
                if res.status_code == 200:
                    self.success.emit(res.json())
                else:
                    self.failed.emit(res.text)
        except Exception as e:
            self.failed.emit(str(e))

class AddDownloadDialog(QDialog):
    def __init__(
        self,
        parent=None,
        initial_url: str = "",
        initial_format: Optional[str] = None,
        initial_cookies: Optional[str] = None,
        initial_folder: Optional[str] = None,
        initial_title: Optional[str] = None
    ):
        super().__init__(parent)
        self.setObjectName("addDownloadDialog")
        self.setWindowTitle("Thêm URL Tải Xuống - Vortex Downloader")
        self.setMinimumWidth(620)
        self.setAutoFillBackground(True)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#f8fafc"))
        pal.setColor(QPalette.WindowText, QColor("#1e293b"))
        pal.setColor(QPalette.Base, QColor("#ffffff"))
        pal.setColor(QPalette.Text, QColor("#1e293b"))
        self.setPalette(pal)

        # Luôn nổi lên trên cùng (đè lên trình duyệt Chrome/Edge)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setStyleSheet(LIGHT_THEME_QSS)

        self.download_task_created = None
        self.extracted_formats = []
        self.initial_format = initial_format
        self.initial_cookies = initial_cookies
        self.initial_title = initial_title
        self.analyze_worker: Optional[AnalyzeWorker] = None
        initial_url = clean_video_url(initial_url)
        self._build_ui(initial_url, initial_folder, initial_title)
        self.loading_overlay = LoadingOverlay(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "loading_overlay") and self.loading_overlay:
            self.loading_overlay.setGeometry(self.rect())

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = int(self.winId())
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception:
                pass

    def _build_ui(self, initial_url: str, initial_folder: Optional[str] = None, initial_title: Optional[str] = None):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # 1. URL Input
        layout.addWidget(QLabel("<b>Đường dẫn URL tải xuống:</b>"))
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit(initial_url)
        self.url_input.setPlaceholderText("https://... (YouTube, TikTok, Facebook, hoặc file .zip/.iso)")
        self.url_input.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(self.url_input)

        self.btn_analyze = QPushButton("🔍 Phân tích Video")
        self.btn_analyze.clicked.connect(self._start_async_analysis)
        url_layout.addWidget(self.btn_analyze)
        layout.addLayout(url_layout)

        # Video info banner
        self.lbl_video_info = QLabel("")
        self.lbl_video_info.setStyleSheet("color: #065f46; font-weight: bold; background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 6px 10px; border-radius: 6px;")
        if initial_title:
            self.lbl_video_info.setText(f"🎬 {initial_title}")
            self.lbl_video_info.setVisible(True)
        else:
            self.lbl_video_info.setVisible(False)
        layout.addWidget(self.lbl_video_info)

        # 2. Format selector (Chọn chất lượng video mong muốn)
        self.format_layout = QVBoxLayout()
        self.lbl_format = QLabel("<b>🎯 Chọn độ phân giải muốn tải (Chỉ tải 1 bản, không tải thừa):</b>")
        self.combo_format = QComboBox()
        self.combo_format.setStyleSheet("padding: 8px;")

        # Nạp ngay danh sách preset chuẩn để UI có sẵn lập tức, không cần đợi mạng
        for label, fmt in STANDARD_PRESETS:
            self.combo_format.addItem(label, fmt)

        self.combo_format.currentIndexChanged.connect(self._on_format_changed)
        self.format_layout.addWidget(self.lbl_format)
        self.format_layout.addWidget(self.combo_format)
        layout.addLayout(self.format_layout)

        # 3. Save Directory
        layout.addWidget(QLabel("<b>Thư mục lưu trữ:</b>"))
        dir_layout = QHBoxLayout()
        
        default_dir = initial_folder if (initial_folder and os.path.exists(initial_folder)) else None
        if not default_dir:
            default_dir = get_default_download_dir()
        os.makedirs(default_dir, exist_ok=True)
        self.dir_input = QLineEdit(default_dir)
        dir_layout.addWidget(self.dir_input)

        self.btn_browse = QPushButton("📁 Chọn thư mục")
        self.btn_browse.clicked.connect(self._browse_dir)
        dir_layout.addWidget(self.btn_browse)
        layout.addLayout(dir_layout)

        # 4. Settings (Threads & Filename)
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Số luồng tải (Threads):"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 32)
        self.spin_threads.setValue(16)
        settings_layout.addWidget(self.spin_threads)

        # Tự động nhận diện định dạng gốc từ URL
        clean_u = initial_url.split("?")[0].split("#")[0].lower()
        detected_ext = ".mp4"
        for candidate in [".ts", ".m3u8", ".webm", ".mkv", ".avi", ".mov", ".flv", ".mp3", ".m4a", ".zip", ".rar", ".iso"]:
            if clean_u.endswith(candidate) or candidate in clean_u:
                detected_ext = ".ts" if candidate in (".ts", ".m3u8") else candidate
                break
        self.detected_source_ext = detected_ext

        settings_layout.addSpacing(20)
        settings_layout.addWidget(QLabel("Tên file:"))
        self.filename_input = QLineEdit()
        if initial_title:
            safe = sanitize_filename(initial_title)
            base, old_ext = os.path.splitext(safe)
            if old_ext and len(old_ext) <= 5:
                safe = base
            ext = ".mp3" if (self.initial_format == "audio_only") else detected_ext
            self.filename_input.setText(f"{safe}{ext}")
        else:
            self.filename_input.setPlaceholderText("Tự động lấy tiêu đề thực của video...")
        settings_layout.addWidget(self.filename_input, 1)
        layout.addLayout(settings_layout)

        # Chọn đúng định dạng ban đầu sau khi đã khởi tạo filename_input
        self._select_matching_format(self.initial_format)

        # 5. Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_download = QPushButton("🚀 Bắt đầu tải ngay")
        self.btn_download.setObjectName("btnPrimary")
        self.btn_download.clicked.connect(self._start_download)
        btn_layout.addWidget(self.btn_download)

        layout.addLayout(btn_layout)

    def _select_matching_format(self, target: Optional[str]):
        if not target:
            return
        target = str(target).strip()
        matched_idx = -1

        # 1. Định dạng chỉ tải âm thanh (Audio Only)
        if target == "audio_only" or target in ("bestaudio", "mp3") or target.startswith("audio_"):
            for idx in range(self.combo_format.count()):
                if self.combo_format.itemData(idx) == "audio_only":
                    matched_idx = idx
                    break

        # 2. Chất lượng tốt nhất (Best Quality)
        elif target in ("bestvideo+bestaudio/best", "best", "bestquality"):
            for idx in range(self.combo_format.count()):
                if self.combo_format.itemData(idx) == "bestvideo+bestaudio/best":
                    matched_idx = idx
                    break

        # 3. Video độ phân giải cụ thể (ví dụ height<=1080, 1080p, v.v.)
        else:
            h_match = re.search(r'height<=?(\d+)', target) or re.search(r'(\d+)p', target)
            if h_match:
                target_h = int(h_match.group(1))
                for idx in range(self.combo_format.count()):
                    data_val = str(self.combo_format.itemData(idx) or "")
                    text = self.combo_format.itemText(idx)
                    if f"<={target_h}]" in data_val or re.search(rf'\b{target_h}p\b', text):
                        matched_idx = idx
                        break

                # Nếu chưa có trong danh sách chuẩn, tự động chèn vào vị trí thích hợp
                if matched_idx == -1:
                    badge = f"🎬 {target_h}p (8K UHD)" if target_h >= 4320 else (
                        f"🎬 {target_h}p (4K UHD)" if target_h >= 2160 else f"📺 {target_h}p"
                    )
                    fmt_val = f"bestvideo[height<={target_h}]+bestaudio/best"
                    self.combo_format.insertItem(1, badge, fmt_val)
                    matched_idx = 1
            else:
                # Tìm kiếm trực tiếp theo itemData
                for idx in range(self.combo_format.count()):
                    if self.combo_format.itemData(idx) == target:
                        matched_idx = idx
                        break

        if matched_idx >= 0 and matched_idx < self.combo_format.count():
            self.combo_format.blockSignals(True)
            self.combo_format.setCurrentIndex(matched_idx)
            self.combo_format.blockSignals(False)
            self._on_format_changed(matched_idx)

    def _on_format_changed(self, index: int):
        if not hasattr(self, "filename_input") or not self.filename_input:
            return
        fmt_data = str(self.combo_format.itemData(index) or "")
        cur_name = self.filename_input.text().strip()
        if not cur_name:
            return
        base, ext = os.path.splitext(cur_name)
        if fmt_data == "audio_only":
            self.filename_input.setText(f"{base}.mp3")
        elif ext.lower() == ".mp3":
            orig = getattr(self, "detected_source_ext", ".ts" if ".m3u8" in self.url_input.text().lower() else ".mp4")
            self.filename_input.setText(f"{base}{orig}")

    def _on_url_changed(self, text: str):
        text = text.strip()
        if not text:
            self.lbl_video_info.setVisible(False)

    def _browse_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu trữ", self.dir_input.text())
        if folder:
            norm = os.path.normpath(folder)
            self.dir_input.setText(norm)

    def _start_async_analysis(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đường link URL!")
            return

        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("⏳ Đang phân tích...")
        self.loading_overlay.show_message("Đang phân tích thông tin video...")

        # Chạy trong luồng phụ (QThread) để tuyệt đối không bao giờ làm đơ giao diện
        self.analyze_worker = AnalyzeWorker(url, self.initial_cookies)
        self.analyze_worker.success.connect(self._on_analysis_success)
        self.analyze_worker.failed.connect(self._on_analysis_failed)
        self.analyze_worker.start()

    def _on_analysis_success(self, data: dict):
        self.loading_overlay.hide_overlay()
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔍 Phân tích Video")

        title = data.get("title", "Video")
        formats = data.get("formats", [])
        self.extracted_formats = formats

        safe_name = sanitize_filename(title)
        base, _ = os.path.splitext(safe_name)
        is_audio = (self.combo_format.currentData() == "audio_only")

        # Giữ nguyên định dạng gốc của nguồn (.ts, .webm, .mkv...), không ép về .mp4
        source_ext = data.get("ext")
        clean_u = self.url_input.text().split("?")[0].split("#")[0].lower()
        if ".m3u8" in clean_u or ".ts" in clean_u:
            source_ext = "ts"
        elif not source_ext or source_ext == "mp4":
            source_ext = getattr(self, "detected_source_ext", ".mp4").lstrip(".")
        
        self.detected_source_ext = f".{source_ext}"
        ext = ".mp3" if is_audio else f".{source_ext}"
        self.filename_input.setText(f"{base}{ext}")

        self.lbl_video_info.setText(f"🎬 {title}")
        self.lbl_video_info.setVisible(True)

        # Xử lý trường hợp file trực tiếp hoặc luồng m3u8/ts đơn lẻ
        if len(formats) == 1 and formats[0].get("format_id") == "direct_file":
            self.combo_format.blockSignals(True)
            self.combo_format.clear()
            size_str = format_approx_size(formats[0].get("filesize_approx"))
            self.combo_format.addItem(f"⚡ Tải trực tiếp đa luồng (16 Threads){size_str}", "direct_file")
            self.combo_format.addItem("🎵 Chỉ tải Âm thanh (Audio MP3)", "audio_only")
            self.combo_format.blockSignals(False)
            return

        url_lower = self.url_input.text().lower()
        if ".m3u8" in url_lower or ".ts" in url_lower:
            self.combo_format.blockSignals(True)
            self.combo_format.clear()
            self.combo_format.addItem("🎬 Luồng phim HLS / .TS (Tự động tải & ghép sang MP4)", "bestvideo+bestaudio/best")
            self.combo_format.addItem("🎵 Chỉ tải Âm thanh (Audio MP3)", "audio_only")
            self.combo_format.blockSignals(False)
            return

        # Lọc và nhóm các độ phân giải theo thứ tự từ cao đến thấp
        unique_resolutions = {}
        for f in formats:
            res_str = f.get("resolution")
            fmt_id = f.get("format_id")
            vcodec = f.get("vcodec")
            size_str = format_approx_size(f.get("filesize_approx"))

            if res_str and "x" in res_str and vcodec != "none":
                height_match = re.search(r'x(\d+)', res_str)
                height = int(height_match.group(1)) if height_match else 0
                if height not in unique_resolutions:
                    unique_resolutions[height] = (res_str, fmt_id, size_str)

        if unique_resolutions:
            current_choice = self.combo_format.currentData()
            self.combo_format.blockSignals(True)
            self.combo_format.clear()
            self.combo_format.addItem("🌟 Tự động chọn chất lượng cao nhất (Best Quality)", "bestvideo+bestaudio/best")

            for h in sorted(unique_resolutions.keys(), reverse=True):
                res_str, fmt_id, size_str = unique_resolutions[h]
                label = f"📺 {h}p ({res_str}){size_str}"
                self.combo_format.addItem(label, f"bestvideo[height<={h}]+bestaudio/best")

            self.combo_format.addItem("🎵 Chỉ tải Âm thanh (Audio MP3)", "audio_only")
            self._select_matching_format(current_choice)
            self.combo_format.blockSignals(False)

    def _on_analysis_failed(self, err: str):
        self.loading_overlay.hide_overlay()
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔍 Phân tích Video")

        url = self.url_input.text().strip()
        url_lower = url.lower()
        if any(url_lower.endswith(ext) or ext in url_lower for ext in [".mp4", ".mkv", ".webm", ".ts", ".m3u8", ".zip", ".iso"]):
            self.lbl_video_info.setText("⚡ Nhận diện tệp tin / luồng stream (Sẵn sàng tải)")
            self.lbl_video_info.setVisible(True)

    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đường link URL!")
            return

        selected_format = self.combo_format.currentData() or self.initial_format
        filename_val = self.filename_input.text().strip() or None
        save_folder = self.dir_input.text().strip()

        payload = {
            "url": url,
            "save_path": save_folder,
            "file_name": filename_val,
            "num_threads": self.spin_threads.value(),
            "format_id": selected_format
        }
        if self.initial_cookies:
            payload["cookies"] = self.initial_cookies

        self.btn_download.setEnabled(False)
        self.btn_download.setText("⏳ Đang bắt đầu...")
        self.loading_overlay.show_message("Đang khởi tạo tiến trình tải...")

        # Chạy khởi tạo task tải trong luồng phụ để cửa sổ đóng mượt mà, không giật lag
        self.starter_worker = DownloadStarterWorker(payload)
        self.starter_worker.success.connect(self._on_download_started)
        self.starter_worker.failed.connect(self._on_download_failed)
        self.starter_worker.start()

    def _on_download_started(self, data: dict):
        self.loading_overlay.hide_overlay()
        self.download_task_created = data
        self.accept()

    def _on_download_failed(self, err: str):
        self.loading_overlay.hide_overlay()
        self.btn_download.setEnabled(True)
        self.btn_download.setText("🚀 Bắt đầu tải ngay")
        QMessageBox.critical(self, "Lỗi kết nối", f"Không thể bắt đầu tải: {err}")
