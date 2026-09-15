import math
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size: int = 40):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)

    def start(self):
        self._angle = 0
        self._timer.start(35)

    def stop(self):
        self._timer.stop()

    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        center_x = w / 2.0
        center_y = h / 2.0
        radius = (min(w, h) - 8) / 2.0

        # Vẽ vòng xoay với 12 vạch tròn mờ dần theo góc
        num_lines = 12
        for i in range(num_lines):
            angle = (self._angle + i * (360 / num_lines)) % 360
            rad = math.radians(angle)
            
            alpha = int(255 * (i + 1) / num_lines)
            pen = QPen(QColor(37, 99, 235, alpha))  # Màu #2563eb Royal Blue
            pen.setWidthF(3.2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)

            r_in = radius * 0.55
            r_out = radius
            x1 = center_x + r_in * math.cos(rad)
            y1 = center_y + r_in * math.sin(rad)
            x2 = center_x + r_out * math.cos(rad)
            y2 = center_y + r_out * math.sin(rad)
            painter.drawLine(x1, y1, x2, y2)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # Hộp card nổi sang trọng ở giữa
        self.card = QWidget(self)
        self.card.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1.5px solid #93c5fd;
                border-radius: 14px;
            }
        """)
        self.card.setFixedSize(260, 110)

        card_layout = QVBoxLayout(self.card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(12)

        self.spinner = LoadingSpinner(self.card, size=38)
        card_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        self.lbl_text = QLabel("Đang xử lý...")
        self.lbl_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #1e293b;
                border: none;
                background: transparent;
            }
        """)
        self.lbl_text.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_text)

        layout.addWidget(self.card)

    def show_message(self, text: str = "Đang xử lý..."):
        self.lbl_text.setText(text)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        self.show()
        self.spinner.start()

    def hide_overlay(self):
        self.spinner.stop()
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Làm mờ nền nhẹ nhàng để tập trung vào hộp loading
        painter.fillRect(self.rect(), QColor(15, 23, 42, 65))
        super().paintEvent(event)

class AsyncActionWorker(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, action_func, *args, **kwargs):
        super().__init__()
        self.action_func = action_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.action_func(*self.args, **self.kwargs)
            self.finished_signal.emit(True, "")
        except Exception as e:
            self.finished_signal.emit(False, str(e))
