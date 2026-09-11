DARK_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #181825;
    color: #cdd6f4;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #cdd6f4;
    background-color: transparent;
}

QHeaderView::section {
    background-color: #1e1e2e;
    color: #a6adc8;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #313244;
    font-weight: bold;
    font-size: 12px;
}

QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
    selection-background-color: #313244;
    selection-color: #89b4fa;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #24273a;
}

QTableWidget::item:selected {
    background-color: #313244;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#btnPrimary {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
}

QPushButton#btnPrimary:hover {
    background-color: #b4befe;
}

QPushButton#btnSuccess {
    background-color: #a6e3a1;
    color: #11111b;
    border: none;
}

QPushButton#btnSuccess:hover {
    background-color: #94e2d5;
}

QPushButton#btnDanger {
    background-color: #f38ba8;
    color: #11111b;
    border: none;
}

QPushButton#btnDanger:hover {
    background-color: #eba0ac;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QProgressBar {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 4px;
    text-align: center;
    color: #cdd6f4;
    font-size: 11px;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #89b4fa, stop:1 #a6e3a1);
    border-radius: 3px;
}

QStatusBar {
    background-color: #1e1e2e;
    border-top: 1px solid #313244;
    color: #a6adc8;
}

QMenu {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #313244;
    color: #89b4fa;
}
"""
