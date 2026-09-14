import sys
import os
import re
import subprocess
import httpx
from typing import Dict, Set, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QHeaderView, QMessageBox, QMenu, QSystemTrayIcon, QStyle,
    QApplication, QButtonGroup, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt, Slot, QRectF
from PySide6.QtGui import QIcon, QPixmap, QImage, QPainter, QPainterPath, QGuiApplication, QCursor, QColor

from client.desktop_gui.styles import DARK_THEME_QSS
from client.desktop_gui.websocket_worker import WebSocketProgressWorker
from client.desktop_gui.add_dialog import AddDownloadDialog, GATEWAY_URL
from client.desktop_gui.loading_overlay import LoadingOverlay, AsyncActionWorker

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
        self._action_workers = []

        self._init_ui()
        self.loading_overlay = LoadingOverlay(self.centralWidget())
        self._init_system_tray()
        self._init_websocket()
        self._init_clipboard_monitor()
        self._load_tasks_from_gateway()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "loading_overlay") and self.loading_overlay:
            self.loading_overlay.setGeometry(self.centralWidget().rect())

    def _run_with_loading(self, message: str, action_func, on_finished=None):
        """Chạy một tác vụ mạng/hệ thống trong luồng phụ và hiển thị overlay loading quay mượt mà"""
        self.loading_overlay.show_message(message)
        worker = AsyncActionWorker(action_func)
        def _on_done(ok, err):
            self.loading_overlay.hide_overlay()
            if worker in self._action_workers:
                self._action_workers.remove(worker)
            if on_finished:
                on_finished(ok, err)
        worker.finished_signal.connect(_on_done)
        self._action_workers.append(worker)
        worker.start()

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

        self.btn_change_folder = QPushButton("⚙ Đổi thư mục")
        self.btn_change_folder.setToolTip("Chọn thư mục lưu tải về mặc định cho máy tính")
        self.btn_change_folder.clicked.connect(self._change_default_download_folder)
        toolbar_layout.addWidget(self.btn_change_folder)

        self.btn_cookies = QPushButton("🍪 Cookies YouTube")
        self.btn_cookies.setToolTip("Nhập tệp cookies.txt từ trình duyệt để vượt qua cơ chế chặn bot của YouTube")
        self.btn_cookies.clicked.connect(self._import_cookies_dialog)
        toolbar_layout.addWidget(self.btn_cookies)

        toolbar_layout.addStretch()

        # Batch action buttons
        self.btn_select_all = QPushButton("☑ Chọn tất cả")
        self.btn_select_all.clicked.connect(self._select_all_tasks)
        toolbar_layout.addWidget(self.btn_select_all)

        self.btn_delete_selected = QPushButton("🗑 Xoá đã chọn")
        self.btn_delete_selected.setObjectName("btnDanger")
        self.btn_delete_selected.clicked.connect(self._delete_selected_batch)
        self.btn_delete_selected.setVisible(False)
        toolbar_layout.addWidget(self.btn_delete_selected)

        self.btn_filter_all = QPushButton("Tất cả (Lịch sử)")
        self.btn_filter_downloading = QPushButton("⚡ Đang tải")
        self.btn_filter_completed = QPushButton("✅ Hoàn tất")
        self.btn_filter_failed = QPushButton("⚠ Lỗi")
        self.btn_filter_paused = QPushButton("⏸ Tạm dừng")

        for btn in [self.btn_filter_all, self.btn_filter_downloading, self.btn_filter_completed, self.btn_filter_failed, self.btn_filter_paused]:
            btn.setCheckable(True)
            toolbar_layout.addWidget(btn)

        self.btn_filter_all.setChecked(True)
        self.btn_filter_all.setStyleSheet("background-color: #89b4fa; color: #11111b;")

        self.filter_group = QButtonGroup(self)
        self.filter_group.addButton(self.btn_filter_all)
        self.filter_group.addButton(self.btn_filter_downloading)
        self.filter_group.addButton(self.btn_filter_completed)
        self.filter_group.addButton(self.btn_filter_failed)
        self.filter_group.addButton(self.btn_filter_paused)

        self.btn_filter_all.clicked.connect(lambda: self._set_filter("all"))
        self.btn_filter_downloading.clicked.connect(lambda: self._set_filter("downloading"))
        self.btn_filter_completed.clicked.connect(lambda: self._set_filter("completed"))
        self.btn_filter_failed.clicked.connect(lambda: self._set_filter("failed"))
        self.btn_filter_paused.clicked.connect(lambda: self._set_filter("paused"))

        main_layout.addLayout(toolbar_layout)

        # 3. Main Tasks Table (7 columns: checkbox + 6 data columns)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "", "Tên Tệp", "Dung lượng", "Tiến độ", "Tốc độ", "Thời gian còn", "Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 36)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 220)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.cellDoubleClicked.connect(self._on_table_double_clicked)
        main_layout.addWidget(self.table)

        # 4. Batch Action Bar (bottom)
        batch_bar = QHBoxLayout()
        batch_bar.setSpacing(8)

        self.btn_delete_completed = QPushButton("✅ Xoá tất cả Hoàn tất")
        self.btn_delete_completed.setObjectName("btnDanger")
        self.btn_delete_completed.clicked.connect(self._delete_all_completed)
        batch_bar.addWidget(self.btn_delete_completed)

        self.btn_delete_failed = QPushButton("⚠ Xoá tất cả Lỗi")
        self.btn_delete_failed.setObjectName("btnDanger")
        self.btn_delete_failed.clicked.connect(self._delete_all_failed)
        batch_bar.addWidget(self.btn_delete_failed)

        batch_bar.addStretch()
        main_layout.addLayout(batch_bar)

    def _set_filter(self, filter_name: str):
        self.current_filter = filter_name
        for btn in [self.btn_filter_all, self.btn_filter_downloading, self.btn_filter_completed, self.btn_filter_failed, self.btn_filter_paused]:
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
        # 1. Xử lý khi có yêu cầu mở hộp thoại từ Extension
        if data.get("type") == "open_add_dialog":
            url = data.get("url", "")
            fmt = data.get("format_id")
            cookies = data.get("cookies")
            save_path = data.get("save_path")
            title = data.get("title")

            self.showNormal()
            self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.raise_()
            self.activateWindow()

            if sys.platform == "win32":
                try:
                    import ctypes
                    hwnd = int(self.winId())
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass

            self._open_add_dialog(
                initial_url=url,
                initial_format=fmt,
                initial_cookies=cookies,
                initial_folder=save_path,
                initial_title=title
            )
            return

        # 2. Xử lý khi có thông báo task bị xóa
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
            elif self.current_filter == "failed" and status == "failed":
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

                # Cột 0: Checkbox
                cb_widget = QWidget()
                cb_layout = QHBoxLayout(cb_widget)
                cb_layout.setContentsMargins(0, 0, 0, 0)
                cb_layout.setAlignment(Qt.AlignCenter)
                cb = QCheckBox()
                cb.setProperty("task_id", task_id)
                cb.stateChanged.connect(self._on_checkbox_changed)
                cb_layout.addWidget(cb)
                self.table.setCellWidget(row, 0, cb_widget)

                item_name = QTableWidgetItem(filename)
                item_name.setData(Qt.UserRole, task_id)
                self.table.setItem(row, 1, item_name)
                self.table.setItem(row, 2, QTableWidgetItem(format_bytes(total_bytes)))

                pbar = QProgressBar()
                pbar.setValue(int(progress))
                self.table.setCellWidget(row, 3, pbar)

                speed_str = "Ghép nối ⚡" if status == "MERGING" else (f"{format_bytes(int(speed))}/s" if speed > 0 else "--")
                self.table.setItem(row, 4, QTableWidgetItem(speed_str))

                eta_str = "Sắp xong" if status == "MERGING" else (f"{int(eta)}s" if (eta is not None and speed > 0) else "--")
                self.table.setItem(row, 5, QTableWidgetItem(eta_str))

                status_item = QTableWidgetItem(status)
                err_msg = t.get("error_message")
                if err_msg:
                    status_item.setToolTip(f"Chi tiết: {err_msg}")
                if status == "FAILED":
                    status_item.setForeground(QColor("#f38ba8"))
                    status_item.setText("FAILED ⚠️")
                elif status == "COMPLETED":
                    status_item.setForeground(QColor("#a6e3a1"))
                elif status == "MERGING":
                    status_item.setForeground(QColor("#f9e2af"))
                    status_item.setText("⚡ Ghép nối (FFmpeg)")
                self.table.setItem(row, 6, status_item)
            else:
                row = self.tasks_row_map[task_id]
                self.table.item(row, 1).setText(filename)
                self.table.item(row, 2).setText(format_bytes(total_bytes))

                pbar = self.table.cellWidget(row, 3)
                if pbar:
                    pbar.setValue(int(progress))

                speed_str = "Ghép nối ⚡" if status == "MERGING" else (f"{format_bytes(int(speed))}/s" if speed > 0 else "--")
                self.table.item(row, 4).setText(speed_str)

                eta_str = "Sắp xong" if status == "MERGING" else (f"{int(eta)}s" if (eta is not None and speed > 0) else "--")
                self.table.item(row, 5).setText(eta_str)

                status_item = self.table.item(row, 6)
                err_msg = t.get("error_message")
                if err_msg:
                    status_item.setToolTip(f"Chi tiết: {err_msg}")
                if status == "FAILED":
                    status_item.setForeground(QColor("#f38ba8"))
                    status_item.setText("FAILED ⚠️")
                elif status == "COMPLETED":
                    status_item.setForeground(QColor("#a6e3a1"))
                    status_item.setText(status)
                elif status == "MERGING":
                    status_item.setForeground(QColor("#f9e2af"))
                    status_item.setText("⚡ Ghép nối (FFmpeg)")
                else:
                    status_item.setForeground(QColor("#cdd6f4"))
                    status_item.setText(status)

        self._update_batch_button_visibility()

    def _on_checkbox_changed(self):
        """Cập nhật hiển thị nút xoá đã chọn khi có checkbox thay đổi"""
        self._update_batch_button_visibility()

    def _get_checked_task_ids(self) -> list:
        """Lấy danh sách task_id của các checkbox đã tick"""
        checked = []
        for row in range(self.table.rowCount()):
            cb_widget = self.table.cellWidget(row, 0)
            if cb_widget:
                cb = cb_widget.findChild(QCheckBox)
                if cb and cb.isChecked():
                    item = self.table.item(row, 1)
                    if item:
                        checked.append(item.data(Qt.UserRole))
        return checked

    def _update_batch_button_visibility(self):
        """Hiện/ẩn nút xoá đã chọn tuỳ theo số checkbox đã tick"""
        checked = self._get_checked_task_ids()
        if checked:
            self.btn_delete_selected.setText(f"🗑 Xoá {len(checked)} đã chọn")
            self.btn_delete_selected.setVisible(True)
        else:
            self.btn_delete_selected.setVisible(False)

    def _select_all_tasks(self):
        """Đảo trạng thái chọn tất cả checkbox"""
        checked = self._get_checked_task_ids()
        all_count = self.table.rowCount()
        select = len(checked) < all_count  # Nếu chưa chọn hết thì chọn hết, ngược lại bỏ chọn
        for row in range(all_count):
            cb_widget = self.table.cellWidget(row, 0)
            if cb_widget:
                cb = cb_widget.findChild(QCheckBox)
                if cb:
                    cb.setChecked(select)
        if select:
            self.btn_select_all.setText("☐ Bỏ chọn tất cả")
        else:
            self.btn_select_all.setText("☑ Chọn tất cả")

    def _delete_batch(self, task_ids: list):
        """Xoá hàng loạt các task theo danh sách ID siêu tốc không giật lag"""
        if not task_ids:
            return

        # 🚀 1. Lập tức ẩn khỏi bảng ở 0ms để người dùng thấy phản hồi ngay
        for tid in task_ids:
            self.deleted_task_ids.add(tid)
            self.all_tasks_cache.pop(tid, None)
        self._render_filtered_tasks()

        count = len(task_ids)
        msg = f"Đang xoá {count} tác vụ..." if count > 1 else "Đang xoá tác vụ..."

        def _do_batch_api_delete():
            try:
                with httpx.Client(timeout=4.0) as client:
                    client.post(f"{GATEWAY_URL}/api/v1/tasks/batch_delete", json={"task_ids": task_ids})
            except Exception:
                pass

        self._run_with_loading(msg, _do_batch_api_delete)

    def _delete_selected_batch(self):
        """Xoá các task đã được tick checkbox"""
        checked = self._get_checked_task_ids()
        if not checked:
            return
        confirm = QMessageBox.question(
            self,
            "Xác nhận xoá hàng loạt",
            f"Bạn có chắc muốn xoá {len(checked)} tác vụ đã chọn?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self._delete_batch(checked)
            self.btn_select_all.setText("☑ Chọn tất cả")

    def _delete_all_completed(self):
        """Xoá tất cả task có trạng thái completed"""
        completed_ids = [
            tid for tid, t in self.all_tasks_cache.items()
            if str(t.get("status", "")).lower() == "completed"
            and tid not in self.deleted_task_ids
        ]
        if not completed_ids:
            QMessageBox.information(self, "Thông báo", "Không có tác vụ hoàn tất nào để xoá.")
            return
        confirm = QMessageBox.question(
            self,
            "Xác nhận xoá",
            f"Xoá {len(completed_ids)} tác vụ đã hoàn tất khỏi danh sách?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self._delete_batch(completed_ids)

    def _delete_all_failed(self):
        """Xoá tất cả task có trạng thái failed"""
        failed_ids = [
            tid for tid, t in self.all_tasks_cache.items()
            if str(t.get("status", "")).lower() == "failed"
            and tid not in self.deleted_task_ids
        ]
        if not failed_ids:
            QMessageBox.information(self, "Thông báo", "Không có tác vụ lỗi nào để xoá.")
            return
        confirm = QMessageBox.question(
            self,
            "Xác nhận xoá",
            f"Xoá {len(failed_ids)} tác vụ bị lỗi khỏi danh sách?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self._delete_batch(failed_ids)

    def _on_table_double_clicked(self, row, col):
        if col == 0:  # Bỏ qua double-click trên cột checkbox
            return
        item = self.table.item(row, 1)
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

    def _open_add_dialog(
        self,
        initial_url: str = "",
        initial_format: Optional[str] = None,
        initial_cookies: Optional[str] = None,
        initial_folder: Optional[str] = None,
        initial_title: Optional[str] = None
    ):
        # PyQt QPushButton.clicked passes checked: bool
        if isinstance(initial_url, bool):
            initial_url = ""

        if not initial_url:
            clip = QGuiApplication.clipboard().text().strip()
            if clip.startswith("http://") or clip.startswith("https://"):
                initial_url = clip

        dlg = AddDownloadDialog(
            self,
            initial_url=initial_url,
            initial_format=initial_format,
            initial_cookies=initial_cookies,
            initial_folder=initial_folder,
            initial_title=initial_title
        )
        if dlg.exec():
            task = dlg.download_task_created
            if task:
                self.all_tasks_cache[task["id"]] = task
                self._render_filtered_tasks()

    def _get_selected_task_id(self):
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 1)
            if item:
                return item.data(Qt.UserRole)
        if self.table.rowCount() == 1:
            item = self.table.item(0, 1)
            if item:
                return item.data(Qt.UserRole)
        return None

    def _pause_selected(self):
        task_id = self._get_selected_task_id()
        if not task_id:
            return

        if task_id in self.all_tasks_cache:
            self.all_tasks_cache[task_id]["status"] = "paused"
            self.all_tasks_cache[task_id]["speed_bps"] = 0.0
            self._render_filtered_tasks()

        def _do_pause():
            with httpx.Client(timeout=4.0) as client:
                client.post(f"{GATEWAY_URL}/api/v1/tasks/{task_id}/pause")

        self._run_with_loading("Đang tạm dừng tác vụ...", _do_pause)

    def _resume_selected(self):
        task_id = self._get_selected_task_id()
        if not task_id:
            return

        if task_id in self.all_tasks_cache:
            self.all_tasks_cache[task_id]["status"] = "downloading"
            self._render_filtered_tasks()

        def _do_resume():
            with httpx.Client(timeout=4.0) as client:
                client.post(f"{GATEWAY_URL}/api/v1/tasks/{task_id}/resume")

        self._run_with_loading("Đang tiếp tục tải...", _do_resume)

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

    def _get_current_default_folder(self) -> str:
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{GATEWAY_URL}/api/v1/system/settings")
                if res.status_code == 200:
                    data = res.json()
                    if data.get("default_download_dir"):
                        return data["default_download_dir"]
        except Exception:
            pass
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../downloads"))
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def _open_downloads_root_folder(self):
        folder = self._get_current_default_folder()
        os.makedirs(folder, exist_ok=True)
        subprocess.Popen(f'explorer "{folder}"')

    def _change_default_download_folder(self):
        current_dir = self._get_current_default_folder()
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục lưu tải về mặc định",
            current_dir
        )
        if selected_dir:
            norm = os.path.normpath(selected_dir)
            def _do_save_dir():
                with httpx.Client(timeout=4.0) as client:
                    client.post(f"{GATEWAY_URL}/api/v1/system/settings", json={"default_download_dir": norm})
            
            def _on_saved(ok, err):
                if ok:
                    QMessageBox.information(self, "Đã lưu thư mục", f"Đã đặt thư mục mặc định thành:\n{norm}")
                else:
                    QMessageBox.warning(self, "Lỗi kết nối", f"Không thể lưu thư mục tới Gateway: {err}")

            self._run_with_loading("Đang lưu thư mục mặc định...", _do_save_dir, _on_saved)

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
        if confirm == QMessageBox.Yes:
            self._delete_batch([task_id])

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return

        row = item.row()
        self.table.selectRow(row)

        name_item = self.table.item(row, 1)
        if not name_item:
            return
        task_id = name_item.data(Qt.UserRole)
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
        elif status == "failed":
            act_retry = menu.addAction("🔄 Thử tải lại (Retry)")
            act_retry.triggered.connect(self._retry_selected)
            act_err = menu.addAction("ℹ Xem chi tiết lỗi")
            act_err.triggered.connect(self._view_error_selected)

        act_folder = menu.addAction("📁 Mở thư mục chứa tệp")
        act_folder.triggered.connect(self._open_selected_folder)

        menu.addSeparator()

        act_del = menu.addAction("🗑 Xóa khỏi danh sách")
        act_del.triggered.connect(self._delete_selected)

        # Thêm menu xoá hàng loạt
        checked = self._get_checked_task_ids()
        if len(checked) > 1:
            menu.addSeparator()
            act_batch = menu.addAction(f"🗑 Xoá {len(checked)} tác vụ đã chọn")
            act_batch.triggered.connect(self._delete_selected_batch)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _import_cookies_dialog(self):
        cookie_file, _ = QFileDialog.getOpenFileName(
            self, "Chọn tệp cookies.txt (Netscape format)", "", "Cookie Files (*.txt);;All Files (*)"
        )
        if cookie_file and os.path.exists(cookie_file):
            try:
                with open(cookie_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if content:
                    def _do_sync():
                        with httpx.Client(timeout=6.0) as client:
                            client.post(f"{GATEWAY_URL}/api/v1/cookies/sync", json={"cookies": content})

                    def _on_synced(ok, err):
                        if ok:
                            QMessageBox.information(
                                self, "Thành công", "Đã đồng bộ tệp Cookies thành công! Các tác vụ YouTube giờ đây sẽ vượt qua cơ chế chặn bot."
                            )
                        else:
                            QMessageBox.critical(self, "Lỗi", f"Không thể đồng bộ tệp cookies: {err}")

                    self._run_with_loading("Đang đồng bộ tệp Cookies...", _do_sync, _on_synced)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc tệp cookies: {e}")

    def _view_error_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 1)
        if not item:
            return
        task_id = item.data(Qt.UserRole)
        task = self.all_tasks_cache.get(task_id, {})
        err = task.get("error_message") or "Không có thông tin chi tiết lỗi."
        QMessageBox.warning(self, "Chi Tiết Lỗi Tải", f"Mã tác vụ: {task_id}\n\nNguyên nhân:\n{err}")

    def _retry_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 1)
        if not item:
            return
        task_id = item.data(Qt.UserRole)
        task = self.all_tasks_cache.get(task_id, {})
        url = task.get("url")
        if not url:
            return

        def _do_retry():
            with httpx.Client(timeout=10.0) as client:
                client.post(f"{GATEWAY_URL}/api/v1/download", json={
                    "url": url,
                    "format_id": "bestvideo+bestaudio/best"
                })

        def _on_retried(ok, err):
            if ok:
                self._load_tasks_from_gateway()
                QMessageBox.information(self, "Thông báo", "Đã gửi lại yêu cầu tải!")
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể gửi lệnh tải lại: {err}")

        self._run_with_loading("Đang gửi yêu cầu tải lại...", _do_retry, _on_retried)

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
