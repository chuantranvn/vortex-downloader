import sys
import os
import re
import subprocess
import httpx
from typing import Dict, Set

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QHeaderView, QMessageBox, QMenu, QSystemTrayIcon, QStyle,
    QApplication, QButtonGroup
)
from PySide6.QtCore import Qt, Slot, QRectF
from PySide6.QtGui import QIcon, QPixmap, QImage, QPainter, QPainterPath, QGuiApplication, QCursor

from client.desktop_gui.styles import DARK_THEME_QSS
from client.desktop_gui.websocket_worker import WebSocketProgressWorker
from client.desktop_gui.add_dialog import AddDownloadDialog, GATEWAY_URL

ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/vortex_icon.png"))

def format_bytes(num_bytes: int) -> str:
    if num_bytes <= 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

def get_rounded_pixmap(image_path: str, size: int = 34, radius: float = 8.0) -> QPixmap:
    target = QPixmap(size, size)
    target.fill(Qt.transparent)

    painter = QPainter(target)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), radius, radius)
    painter.setClipPath(path)

    src = QPixmap(image_path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return target

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vortex Downloader - IDM Microservices Engine")
        self.resize(1060, 680)
        self.setStyleSheet(DARK_THEME_QSS)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.tasks_row_map: Dict[str, int] = {}
        self.all_tasks_cache: Dict[str, dict] = {}
        self.deleted_task_ids: Set[str] = set()
        self.current_filter = "all"
        self.last_clipboard_text = ""

        self._init_ui()
        self._init_system_tray()
        self._init_websocket()
        self._init_clipboard_monitor()
        self._load_tasks_from_gateway()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Top Header Bar
        header_layout = QHBoxLayout()
        
        if os.path.exists(ICON_PATH):
            lbl_logo = QLabel()
            lbl_logo.setPixmap(get_rounded_pixmap(ICON_PATH, 34, 8.5))
            header_layout.addWidget(lbl_logo)

        title_label = QLabel("VORTEX DOWNLOADER")
        title_label.setStyleSheet("font-size: 19px; font-weight: bold; color: #89b4fa; letter-spacing: 1.5px; margin-left: 8px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.lbl_speed = QLabel("⚡ 0.0 MB/s")
        self.lbl_speed.setStyleSheet("background-color: #313244; color: #a6e3a1; font-weight: bold; padding: 4px 14px; border-radius: 12px; font-size: 13px;")
        header_layout.addWidget(self.lbl_speed)

        self.lbl_status = QLabel("● Kết nối Gateway")
        self.lbl_status.setStyleSheet("color: #f9e2af; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(self.lbl_status)
        main_layout.addLayout(header_layout)

        # 2. Action Toolbar & Filter Tabs
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.btn_add = QPushButton("＋ Thêm URL")
        self.btn_add.setObjectName("btnPrimary")
        self.btn_add.clicked.connect(self._open_add_dialog)
        toolbar_layout.addWidget(self.btn_add)

        self.btn_open_folder = QPushButton("📁 Thư mục tải về")
        self.btn_open_folder.clicked.connect(self._open_downloads_root_folder)
        toolbar_layout.addWidget(self.btn_open_folder)

        toolbar_layout.addStretch()

        self.btn_filter_all = QPushButton("Tất cả (Lịch sử)")
        self.btn_filter_downloading = QPushButton("⚡ Đang tải")
        self.btn_filter_completed = QPushButton("✅ Hoàn tất")
        self.btn_filter_paused = QPushButton("⏸ Tạm dừng")

        for btn in [self.btn_filter_all, self.btn_filter_downloading, self.btn_filter_completed, self.btn_filter_paused]:
            btn.setCheckable(True)
            toolbar_layout.addWidget(btn)

        self.btn_filter_all.setChecked(True)
        self.btn_filter_all.setStyleSheet("background-color: #89b4fa; color: #11111b;")

        self.filter_group = QButtonGroup(self)
        self.filter_group.addButton(self.btn_filter_all)
        self.filter_group.addButton(self.btn_filter_downloading)
        self.filter_group.addButton(self.btn_filter_completed)
        self.filter_group.addButton(self.btn_filter_paused)

        self.btn_filter_all.clicked.connect(lambda: self._set_filter("all"))
        self.btn_filter_downloading.clicked.connect(lambda: self._set_filter("downloading"))
        self.btn_filter_completed.clicked.connect(lambda: self._set_filter("completed"))
        self.btn_filter_paused.clicked.connect(lambda: self._set_filter("paused"))

        main_layout.addLayout(toolbar_layout)

        # 3. Main Tasks Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Tên Tệp", "Dung lượng", "Tiến độ", "Tốc độ", "Thời gian còn", "Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 220)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.cellDoubleClicked.connect(self._on_table_double_clicked)
        main_layout.addWidget(self.table)

    def _set_filter(self, filter_name: str):
        self.current_filter = filter_name
        for btn in [self.btn_filter_all, self.btn_filter_downloading, self.btn_filter_completed, self.btn_filter_paused]:
            if btn.isChecked():
                btn.setStyleSheet("background-color: #89b4fa; color: #11111b;")
            else:
                btn.setStyleSheet("")
        self._render_filtered_tasks()

    def _init_system_tray(self):
        self.tray = QSystemTrayIcon(self)
        if os.path.exists(ICON_PATH):
            self.tray.setIcon(QIcon(ICON_PATH))
        else:
            self.tray.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        
        tray_menu = QMenu()
        act_show = tray_menu.addAction("Mở Vortex Downloader")
        act_show.triggered.connect(self.showNormal)
        act_add = tray_menu.addAction("Thêm URL mới...")
        act_add.triggered.connect(self._open_add_dialog)
        tray_menu.addSeparator()
        act_quit = tray_menu.addAction("Thoát hoàn toàn")
        act_quit.triggered.connect(self._quit_app)

        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def _init_websocket(self):
        self.ws_worker = WebSocketProgressWorker()
        self.ws_worker.progress_received.connect(self._on_progress_update)
        self.ws_worker.connection_status.connect(self._on_connection_change)
        self.ws_worker.start()

    def _init_clipboard_monitor(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.dataChanged.connect(self._on_clipboard_changed)

    def _on_clipboard_changed(self):
        text = QGuiApplication.clipboard().text().strip()
        if not text or text == self.last_clipboard_text:
            return
        self.last_clipboard_text = text

        if text.startswith("http://") or text.startswith("https://"):
            video_patterns = [
                r"youtube\.com|youtu\.be",
                r"tiktok\.com",
                r"facebook\.com|fb\.watch",
                r"\.(mp4|mkv|zip|iso|exe|tar\.gz|7z|rar|ts|m3u8)(?:\?.*)?$"
            ]
            if any(re.search(p, text, re.IGNORECASE) for p in video_patterns):
                reply = QMessageBox.question(
                    self,
                    "Phát hiện liên kết tải",
                    f"Phát hiện đường link vừa sao chép:\n{text[:80]}...\n\nBạn có muốn tải ngay bây giờ không?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    self.showNormal()
                    self.activateWindow()
                    self._open_add_dialog(initial_url=text)

    @Slot(bool)
    def _on_connection_change(self, is_online: bool):
        if is_online:
            self.lbl_status.setText("● Gateway Online")
            self.lbl_status.setStyleSheet("color: #a6e3a1; font-weight: bold; margin-left: 10px;")
        else:
            self.lbl_status.setText("○ Đang kết nối Gateway...")
            self.lbl_status.setStyleSheet("color: #f38ba8; font-weight: bold; margin-left: 10px;")

    @Slot(dict)
    def _on_progress_update(self, data: dict):
        # 1. Xử lý khi có thông báo task bị xóa
        if data.get("type") == "task_deleted":
            deleted_id = data.get("task_id")
            if deleted_id:
                self.deleted_task_ids.add(deleted_id)
                self.all_tasks_cache.pop(deleted_id, None)
                self._render_filtered_tasks()
            return

        tasks = data.get("tasks", [])
        total_speed = 0.0

        for t in tasks:
            tid = t.get("id")
            # Nếu task đã bị xóa, tuyệt đối không thêm lại
            if tid in self.deleted_task_ids:
                continue
            total_speed += t.get("speed_bps", 0.0)
            self.all_tasks_cache[tid] = t

        self.lbl_speed.setText(f"⚡ {format_bytes(int(total_speed))}/s")
        self._render_filtered_tasks()

    def _load_tasks_from_gateway(self):
        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.get(f"{GATEWAY_URL}/api/v1/tasks")
                if res.status_code == 200:
                    for t in res.json():
                        tid = t["id"]
                        if tid not in self.deleted_task_ids:
                            self.all_tasks_cache[tid] = t
                    self._render_filtered_tasks()
        except Exception:
            pass

    def _render_filtered_tasks(self):
        filtered = []
        for t in self.all_tasks_cache.values():
            tid = t.get("id")
            if tid in self.deleted_task_ids:
                continue
            status = str(t.get("status", "")).lower()
            if self.current_filter == "all":
                filtered.append(t)
            elif self.current_filter == "downloading" and status in ("downloading", "queued", "merging"):
                filtered.append(t)
            elif self.current_filter == "completed" and status == "completed":
                filtered.append(t)
            elif self.current_filter == "paused" and status == "paused":
                filtered.append(t)

        filtered.sort(key=lambda x: x.get("created_at", 0), reverse=True)

        current_ids = [t["id"] for t in filtered]
        existing_ids = list(self.tasks_row_map.keys())

        if current_ids != existing_ids:
            self.table.setRowCount(0)
            self.tasks_row_map.clear()

        for idx, t in enumerate(filtered):
            task_id = t["id"]
            filename = t.get("file_name", "Unknown")
            total_bytes = t.get("total_bytes", 0)
            progress = t.get("progress_percent", 0.0)
            speed = t.get("speed_bps", 0.0)
            eta = t.get("eta_seconds")
            status = str(t.get("status", "queued")).upper()

            if task_id not in self.tasks_row_map:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.tasks_row_map[task_id] = row

                item_name = QTableWidgetItem(filename)
                item_name.setData(Qt.UserRole, task_id)
                self.table.setItem(row, 0, item_name)
                self.table.setItem(row, 1, QTableWidgetItem(format_bytes(total_bytes)))

                pbar = QProgressBar()
                pbar.setValue(int(progress))
                self.table.setCellWidget(row, 2, pbar)

                speed_str = f"{format_bytes(int(speed))}/s" if speed > 0 else "--"
                self.table.setItem(row, 3, QTableWidgetItem(speed_str))

                eta_str = f"{int(eta)}s" if (eta is not None and speed > 0) else "--"
                self.table.setItem(row, 4, QTableWidgetItem(eta_str))
                self.table.setItem(row, 5, QTableWidgetItem(status))
            else:
                row = self.tasks_row_map[task_id]
                self.table.item(row, 0).setText(filename)
                self.table.item(row, 1).setText(format_bytes(total_bytes))

                pbar = self.table.cellWidget(row, 2)
                if pbar:
                    pbar.setValue(int(progress))

                speed_str = f"{format_bytes(int(speed))}/s" if speed > 0 else "--"
                self.table.item(row, 3).setText(speed_str)

                eta_str = f"{int(eta)}s" if (eta is not None and speed > 0) else "--"
                self.table.item(row, 4).setText(eta_str)
                self.table.item(row, 5).setText(status)

    def _on_table_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        if not item:
            return
        task_id = item.data(Qt.UserRole)
        task = self.all_tasks_cache.get(task_id)
        if task:
            path = task.get("save_path")
            if path and os.path.exists(path) and os.path.isfile(path):
                try:
                    os.startfile(path)
                except Exception as e:
                    QMessageBox.warning(self, "Lỗi mở tệp", str(e))
            else:
                self._open_selected_folder()

    def _open_add_dialog(self, initial_url: str = ""):
        if not initial_url:
            clip = QGuiApplication.clipboard().text().strip()
            if clip.startswith("http://") or clip.startswith("https://"):
                initial_url = clip

        dlg = AddDownloadDialog(self, initial_url)
        if dlg.exec():
            task = dlg.download_task_created
            if task:
                self.all_tasks_cache[task["id"]] = task
                self._render_filtered_tasks()

    def _get_selected_task_id(self):
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 0)
            if item:
                return item.data(Qt.UserRole)
        if self.table.rowCount() == 1:
            item = self.table.item(0, 0)
            if item:
                return item.data(Qt.UserRole)
        return None

    def _pause_selected(self):
        task_id = self._get_selected_task_id()
        if not task_id:
            return
        try:
            res = httpx.post(f"{GATEWAY_URL}/api/v1/tasks/{task_id}/pause", timeout=5.0)
            if res.status_code == 200:
                if task_id in self.all_tasks_cache:
                    self.all_tasks_cache[task_id]["status"] = "paused"
                    self.all_tasks_cache[task_id]["speed_bps"] = 0.0
                self._render_filtered_tasks()
            else:
                QMessageBox.warning(self, "Lỗi", f"Không thể tạm dừng: {res.text}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def _resume_selected(self):
        task_id = self._get_selected_task_id()
        if not task_id:
            return
        try:
            res = httpx.post(f"{GATEWAY_URL}/api/v1/tasks/{task_id}/resume", timeout=5.0)
            if res.status_code == 200:
                if task_id in self.all_tasks_cache:
                    self.all_tasks_cache[task_id]["status"] = "downloading"
                self._render_filtered_tasks()
            else:
                QMessageBox.warning(self, "Lỗi", f"Không thể tiếp tục tải: {res.text}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def _open_selected_file(self):
        task_id = self._get_selected_task_id()
        if task_id:
            task = self.all_tasks_cache.get(task_id)
            if task:
                path = task.get("save_path")
                if path and os.path.exists(path) and os.path.isfile(path):
                    try:
                        os.startfile(path)
                        return
                    except Exception as e:
                        QMessageBox.warning(self, "Lỗi", str(e))
        QMessageBox.information(self, "Thông báo", "Tệp tin chưa hoàn tất hoặc không tồn tại.")

    def _open_selected_folder(self):
        task_id = self._get_selected_task_id()
        if task_id:
            task = self.all_tasks_cache.get(task_id)
            if task:
                path = task.get("save_path")
                if path:
                    folder = os.path.dirname(path) if os.path.isfile(path) else path
                    if os.path.exists(folder):
                        subprocess.Popen(f'explorer "{folder}"')
                        return
        self._open_downloads_root_folder()

    def _open_downloads_root_folder(self):
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../downloads"))
        os.makedirs(default_dir, exist_ok=True)
        subprocess.Popen(f'explorer "{default_dir}"')

    def _delete_selected(self):
        task_id = self._get_selected_task_id()
        if not task_id:
            return

        confirm = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa tác vụ này khỏi danh sách?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        # 🚀 ĐÁNH DẤU XÓA VÀ LOẠI BỎ NGAY LẬP TỨC KHỎI GIAO DIỆN
        self.deleted_task_ids.add(task_id)
        self.all_tasks_cache.pop(task_id, None)
        self._render_filtered_tasks()

        try:
            httpx.post(f"{GATEWAY_URL}/api/v1/tasks/{task_id}/cancel", timeout=5.0)
        except Exception:
            pass

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return

        row = item.row()
        self.table.selectRow(row)

        task_id = self.table.item(row, 0).data(Qt.UserRole)
        task = self.all_tasks_cache.get(task_id, {})
        status = str(task.get("status", "")).lower()

        menu = QMenu(self)

        if status in ("downloading", "queued", "merging"):
            act_pause = menu.addAction("⏸ Tạm dừng (Pause)")
            act_pause.triggered.connect(self._pause_selected)
        elif status == "paused":
            act_resume = menu.addAction("▶ Tiếp tục tải (Resume)")
            act_resume.triggered.connect(self._resume_selected)
        elif status == "completed":
            act_open_file = menu.addAction("▶ Mở tệp xem ngay (Open)")
            act_open_file.triggered.connect(self._open_selected_file)

        act_folder = menu.addAction("📁 Mở thư mục chứa tệp")
        act_folder.triggered.connect(self._open_selected_folder)

        menu.addSeparator()

        act_del = menu.addAction("🗑 Xóa khỏi danh sách")
        act_del.triggered.connect(self._delete_selected)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            self.tray.showMessage(
                "Vortex Downloader",
                "Phần mềm vẫn đang chạy ngầm để tiếp tục tải file và lưu lịch sử.",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            self._quit_app()
            event.accept()

    def _quit_app(self):
        self.ws_worker.stop()
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Vortex Downloader")
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
