"""
core/theme.py
=============
Σκούρο θέμα (dark) και βοηθητικά widgets για συνεπή εμφάνιση.
"""

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QFrame

# Παλέτα χρωμάτων (σταθερές για χρήση και στα matplotlib plots)
BG = "#1b1d23"
BG_PANEL = "#23262e"
BG_BASE = "#15171c"
ACCENT = "#00d3a7"      # τιρκουάζ
ACCENT2 = "#ffb454"     # πορτοκαλί
ACCENT3 = "#ff5d8f"     # ροζ/φούξια
ACCENT4 = "#5da9ff"     # μπλε
TEXT = "#e6e6e6"
TEXT_DIM = "#9aa0aa"
GRID = "#3a3f4b"
DANGER = "#ff5050"
GOOD = "#3ddc97"


class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(BG))
        self.setColor(QPalette.WindowText, QColor(TEXT))
        self.setColor(QPalette.Base, QColor(BG_BASE))
        self.setColor(QPalette.AlternateBase, QColor(BG_PANEL))
        self.setColor(QPalette.ToolTipBase, QColor(BG_PANEL))
        self.setColor(QPalette.ToolTipText, QColor(TEXT))
        self.setColor(QPalette.Text, QColor(TEXT))
        self.setColor(QPalette.Button, QColor(BG_PANEL))
        self.setColor(QPalette.ButtonText, QColor(TEXT))
        self.setColor(QPalette.Highlight, QColor(ACCENT))
        self.setColor(QPalette.HighlightedText, QColor("#101216"))
        self.setColor(QPalette.Link, QColor(ACCENT4))


STYLESHEET = f"""
QMainWindow, QWidget {{ background-color: {BG}; color: {TEXT}; font-size: 13px; }}
QGroupBox {{
    border: 1px solid {GRID}; border-radius: 8px; margin-top: 14px;
    padding: 10px 8px 8px 8px; background-color: {BG_PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 12px; padding: 0 6px;
    color: {ACCENT}; font-weight: 600;
}}
QLabel {{ color: {TEXT}; }}
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
    background-color: {BG_BASE}; border: 1px solid {GRID};
    border-radius: 5px; padding: 4px 6px; color: {TEXT};
}}
QComboBox QAbstractItemView {{
    background-color: {BG_BASE}; selection-background-color: {ACCENT};
    selection-color: #101216; color: {TEXT};
}}
QPushButton {{
    background-color: {ACCENT}; color: #0c0e12; border: none;
    border-radius: 6px; padding: 8px 14px; font-weight: 600;
}}
QPushButton:hover {{ background-color: #1ee0bb; }}
QPushButton:pressed {{ background-color: #00a886; }}
QPushButton#secondary {{ background-color: {BG_PANEL}; color: {TEXT}; border: 1px solid {GRID}; }}
QPushButton#secondary:hover {{ background-color: #2c303a; }}
QSlider::groove:horizontal {{ height: 6px; background: {GRID}; border-radius: 3px; }}
QSlider::handle:horizontal {{
    background: {ACCENT}; width: 16px; margin: -6px 0; border-radius: 8px;
}}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 3px; }}
QListWidget {{
    background-color: {BG_BASE}; border: none; outline: 0;
    padding: 6px; font-size: 13px;
}}
QListWidget::item {{ padding: 9px 12px; border-radius: 6px; margin: 2px 4px; color: {TEXT_DIM}; }}
QListWidget::item:selected {{ background-color: {ACCENT}; color: #0c0e12; font-weight: 600; }}
QListWidget::item:hover {{ background-color: {BG_PANEL}; }}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid {GRID}; background: {BG_BASE}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border: 1px solid {ACCENT}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: {BG}; width: 11px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {GRID}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QTabWidget::pane {{ border: 1px solid {GRID}; border-radius: 6px; }}
QTabBar::tab {{
    background: {BG_PANEL}; color: {TEXT_DIM}; padding: 7px 14px;
    border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px;
}}
QTabBar::tab:selected {{ background: {ACCENT}; color: #0c0e12; font-weight: 600; }}
"""


def apply_mpl_style(fig, axes=None):
    """Εφαρμόζει το σκούρο θέμα σε ένα matplotlib Figure/Axes."""
    fig.patch.set_facecolor(BG_PANEL)
    if axes is None:
        axes = fig.get_axes()
    if not isinstance(axes, (list, tuple)):
        axes = [axes]
    for ax in axes:
        ax.set_facecolor(BG_BASE)
        for spine in ax.spines.values():
            spine.set_color(GRID)
        ax.tick_params(colors=TEXT_DIM, labelsize=9)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)
        if hasattr(ax, "zaxis"):
            try:
                ax.zaxis.label.set_color(TEXT)
            except Exception:
                pass


def heading(text, size=15, color=ACCENT):
    lbl = QLabel(text)
    f = QFont()
    f.setPointSize(size)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {color};")
    return lbl


def body(text, color=TEXT_DIM, size=12, wrap=True):
    lbl = QLabel(text)
    lbl.setWordWrap(wrap)
    lbl.setStyleSheet(f"color: {color}; font-size: {size}px;")
    lbl.setTextFormat(Qt.RichText)
    return lbl


def hline():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {GRID}; background: {GRID};")
    line.setFixedHeight(1)
    return line


def group(title):
    g = QGroupBox(title)
    return g
