import os

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))
CHECKMARK_PATH = os.path.join(ASSETS_DIR, "check_white.png").replace("\\", "/")

LIGHT_THEME_QSS = f"""
QMainWindow, QDialog, QWidget#centralWidget, QWidget#mainContentWidget, QDialog#addDownloadDialog {{
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}}

QLabel, QFrame {{
    color: #1e293b;
    background-color: transparent;
}}

/* === SIDEBAR STYLES === */
QWidget#sidebarWidget {{
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}}

QPushButton#sidebarAddButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
    border-radius: 9px;
    padding: 10px 16px;
    font-weight: 700;
    font-size: 13.5px;
    text-align: center;
}}

QPushButton#sidebarAddButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
    background-color: #1d4ed8;
}}

QPushButton#sidebarAddButton:pressed {{
    background-color: #1e40af;
}}

QPushButton#sidebarNavButton {{
    text-align: left;
    padding: 10px 14px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    background-color: transparent;
}}

QPushButton#sidebarNavButton:hover {{
    background-color: #f1f5f9;
    color: #0f172a;
}}

QPushButton#sidebarNavButton:checked {{
    background-color: #eff6ff;
    color: #2563eb;
    font-weight: 700;
}}

QPushButton#sidebarSubButton {{
    text-align: left;
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
    color: #475569;
    background-color: #ffffff;
}}

QPushButton#sidebarSubButton:hover {{
    background-color: #f8fafc;
    border-color: #cbd5e1;
    color: #0f172a;
}}

QPushButton#sidebarSubButton:pressed {{
    background-color: #f1f5f9;
}}

/* === TOP BAR & SEARCH === */
QLineEdit#searchBar {{
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 6px 14px;
    font-size: 12.5px;
}}

QLineEdit#searchBar:focus {{
    border: 1.5px solid #3b82f6;
    background-color: #ffffff;
}}

/* === TABLE STYLING === */
QTableWidget {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    outline: none;
    gridline-color: transparent;
}}

QHeaderView::section {{
    background-color: #f8fafc;
    color: #64748b;
    padding: 11px 14px;
    border: none;
    border-bottom: 1.5px solid #e2e8f0;
    font-weight: 700;
    font-size: 11.5px;
    letter-spacing: 0.5px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 11px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 11px;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
}}

QTableWidget::item:selected {{
    background-color: #eff6ff;
    color: #1e40af;
}}

/* === ROW ACTION BUTTONS === */
QPushButton#rowActionBtn {{
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
}}

QPushButton#rowActionBtn:hover {{
    background-color: #e2e8f0;
    color: #0f172a;
    border-color: #cbd5e1;
}}

QPushButton#rowActionDanger {{
    background-color: #fee2e2;
    color: #dc2626;
    border: 1px solid #fca5a5;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
}}

QPushButton#rowActionDanger:hover {{
    background-color: #fecaca;
}}

/* === GENERAL BUTTONS === */
QPushButton {{
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 12.5px;
}}

QPushButton:hover {{
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}}

QPushButton:pressed {{
    background-color: #e2e8f0;
    border-color: #64748b;
}}

QPushButton#btnPrimary {{
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
    border-radius: 7px;
}}

QPushButton#btnPrimary:hover {{
    background-color: #1d4ed8;
}}

QPushButton#btnPrimary:pressed {{
    background-color: #1e40af;
}}

QPushButton#btnSuccess {{
    background-color: #10b981;
    color: #ffffff;
    border: 1px solid #059669;
    border-radius: 7px;
}}

QPushButton#btnSuccess:hover {{
    background-color: #059669;
}}

QPushButton#btnDanger {{
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    border-radius: 7px;
}}

QPushButton#btnDanger:hover {{
    background-color: #fecaca;
    border-color: #f87171;
    color: #991b1b;
}}

QPushButton#btnDanger:pressed {{
    background-color: #fca5a5;
}}

/* === INPUTS & PROGRESS === */
QLineEdit, QSpinBox, QComboBox {{
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 7px 11px;
    font-size: 13px;
    selection-background-color: #bfdbfe;
    selection-color: #1e3a8a;
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1.5px solid #2563eb;
    background-color: #ffffff;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QProgressBar {{
    background-color: #e2e8f0;
    border: none;
    border-radius: 5px;
    text-align: center;
    color: #0f172a;
    font-size: 10.5px;
    font-weight: 700;
    height: 18px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #10b981);
    border-radius: 5px;
}}

QStatusBar {{
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
}}

QMenu {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    padding: 6px;
}}

QMenu::item {{
    padding: 7px 24px;
    border-radius: 5px;
    color: #1e293b;
}}

QMenu::item:selected {{
    background-color: #eff6ff;
    color: #2563eb;
    font-weight: 600;
}}

QMenu::separator {{
    height: 1px;
    background-color: #e2e8f0;
    margin: 5px 6px;
}}

QCheckBox {{
    spacing: 7px;
    color: #1e293b;
    font-weight: 500;
    background-color: transparent;
}}

QCheckBox#tableCheckbox {{
    spacing: 0px;
    margin: 0px;
    padding: 0px;
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid #94a3b8;
    border-radius: 4px;
    background-color: #ffffff;
}}

QCheckBox::indicator:hover {{
    border-color: #2563eb;
}}

QCheckBox::indicator:checked {{
    background-color: #2563eb;
    border-color: #2563eb;
    image: url("{CHECKMARK_PATH}");
}}

QToolTip {{
    background-color: #0f172a;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}}

QMessageBox {{
    background-color: #f8fafc;
    color: #1e293b;
}}

QMessageBox QLabel {{
    color: #1e293b;
    background-color: transparent;
    font-size: 13px;
    font-weight: 500;
}}
"""

DARK_THEME_QSS = LIGHT_THEME_QSS
