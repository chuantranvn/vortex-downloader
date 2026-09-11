import os
import re
import httpx
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

GATEWAY_URL = "http://localhost:8000"
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/vortex_icon.png"))

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

class AddDownloadDialog(QDialog):
    def __init__(self, parent=None, initial_url: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Thêm URL Tải Xuống - Vortex Downloader")
        self.setMinimumWidth(620)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.download_task_created = None
        self.extracted_formats = []

        self._build_ui(initial_url)

        # Nếu có sẵn URL khi mở, tự động phân tích sau 300ms
        if initial_url and any(domain in initial_url.lower() for domain in ["youtube", "youtu.be", "tiktok", "facebook", "fb.watch", "vimeo"]):
            QTimer.singleShot(300, self._analyze_video)

    def _build_ui(self, initial_url: str):
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
        self.btn_analyze.clicked.connect(self._analyze_video)
        url_layout.addWidget(self.btn_analyze)
        layout.addLayout(url_layout)

        # Video info banner
        self.lbl_video_info = QLabel("")
        self.lbl_video_info.setStyleSheet("color: #a6e3a1; font-weight: bold; background-color: #313244; padding: 6px 10px; border-radius: 6px;")
        self.lbl_video_info.setVisible(False)
        layout.addWidget(self.lbl_video_info)

        # 2. Format selector (Chọn chất lượng video mong muốn)
        self.format_layout = QVBoxLayout()
        self.lbl_format = QLabel("<b>🎯 Chọn độ phân giải muốn tải (Chỉ tải 1 bản, không tải thừa):</b>")
        self.combo_format = QComboBox()
        self.combo_format.setStyleSheet("padding: 8px;")
        self.format_layout.addWidget(self.lbl_format)
        self.format_layout.addWidget(self.combo_format)
        self.lbl_format.setVisible(False)
        self.combo_format.setVisible(False)
        layout.addLayout(self.format_layout)

        # 3. Save Directory
        layout.addWidget(QLabel("<b>Thư mục lưu trữ:</b>"))
        dir_layout = QHBoxLayout()
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../downloads"))
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

        settings_layout.addSpacing(20)
        settings_layout.addWidget(QLabel("Tên file:"))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Tự động lấy tiêu đề thực của video...")
        settings_layout.addWidget(self.filename_input, 1)
        layout.addLayout(settings_layout)

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

    def _on_url_changed(self, text: str):
        # Reset banner và format khi đổi link
        text = text.strip()
        if not text:
            self.lbl_video_info.setVisible(False)
            self.lbl_format.setVisible(False)
            self.combo_format.setVisible(False)

    def _browse_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu trữ", self.dir_input.text())
        if folder:
            self.dir_input.setText(folder)

    def _analyze_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đường link URL!")
            return

        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("⏳ Đang phân tích...")

        try:
            with httpx.Client(timeout=25.0) as client:
                res = client.post(f"{GATEWAY_URL}/api/v1/extract", json={"url": url})
                if res.status_code == 200:
                    data = res.json()
                    title = data.get("title", "Video")
                    formats = data.get("formats", [])
                    self.extracted_formats = formats

                    safe_name = sanitize_filename(title)
                    self.filename_input.setText(f"{safe_name}.mp4")

                    self.lbl_video_info.setText(f"🎬 {title}")
                    self.lbl_video_info.setVisible(True)

                    self.combo_format.clear()
                    self.combo_format.addItem("🌟 Tự động chọn chất lượng cao nhất (Best Quality)", "bestvideo+bestaudio/best")

                    # Lọc và nhóm các độ phân giải theo thứ tự từ cao đến thấp
                    unique_resolutions = {}
                    for f in formats:
                        res_str = f.get("resolution")
                        fmt_id = f.get("format_id")
                        vcodec = f.get("vcodec")
                        size_str = format_approx_size(f.get("filesize_approx"))

                        # Chỉ lấy các format có video
                        if res_str and "x" in res_str and vcodec != "none":
                            height_match = re.search(r'x(\d+)', res_str)
                            height = int(height_match.group(1)) if height_match else 0
                            if height not in unique_resolutions:
                                unique_resolutions[height] = (res_str, fmt_id, size_str)

                    # Sắp xếp từ cao xuống thấp: 2160p (4K), 1440p (2K), 1080p, 720p, 480p, 360p
                    for h in sorted(unique_resolutions.keys(), reverse=True):
                        res_str, fmt_id, size_str = unique_resolutions[h]
                        label = f"📺 {h}p ({res_str}){size_str}"
                        self.combo_format.addItem(label, fmt_id)

                    # Thêm tùy chọn chỉ tải âm thanh
                    self.combo_format.addItem("🎵 Chỉ tải Âm thanh (Audio MP3)", "audio_only")

                    self.lbl_format.setVisible(True)
                    self.combo_format.setVisible(True)
                else:
                    QMessageBox.information(self, "Thông báo", "Đây là link tải file trực tiếp (không phải video streaming).")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi phân tích", f"Không thể phân tích video: {str(e)}")
        finally:
            self.btn_analyze.setEnabled(True)
            self.btn_analyze.setText("🔍 Phân tích Video")

    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đường link URL!")
            return

        selected_format = None
        if self.combo_format.isVisible() and self.combo_format.currentIndex() >= 0:
            selected_format = self.combo_format.currentData()

        filename_val = self.filename_input.text().strip() or None

        payload = {
            "url": url,
            "save_path": self.dir_input.text().strip(),
            "file_name": filename_val,
            "num_threads": self.spin_threads.value(),
            "format_id": selected_format
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{GATEWAY_URL}/api/v1/download", json=payload)
                if res.status_code == 200:
                    self.download_task_created = res.json()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể bắt đầu tải: {res.text}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể kết nối đến Gateway: {str(e)}")
