"""
core/mpl_canvas.py
==================
Βοηθητικά για matplotlib μέσα σε Qt + βασική κλάση module (ModulePage)
με τυποποιημένη διάταξη: αριστερά πίνακας ελέγχου, δεξιά καμβάς.
"""

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
                             QSlider, QLabel, QComboBox, QFormLayout, QSizePolicy)
from PyQt5.QtCore import Qt

from . import theme


class MplCanvas(FigureCanvas):
    """Καμβάς matplotlib με σκούρο θέμα."""

    def __init__(self, nrows=1, ncols=1, projection=None, figsize=(7.2, 5.4)):
        self.fig = Figure(figsize=figsize, tight_layout=True)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.axes = []
        idx = 1
        for _ in range(nrows * ncols):
            proj = projection if not isinstance(projection, (list, tuple)) else projection[idx - 1]
            ax = self.fig.add_subplot(nrows, ncols, idx, projection=proj)
            self.axes.append(ax)
            idx += 1
        theme.apply_mpl_style(self.fig, self.axes)

    @property
    def ax(self):
        return self.axes[0]

    def refresh(self):
        theme.apply_mpl_style(self.fig, self.axes)
        self.draw_idle()


class StyledNavToolbar(NavToolbar):
    """Toolbar πλοήγησης matplotlib με σκούρο φόντο."""
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.setStyleSheet(
            f"background:{theme.BG_PANEL}; border:none; spacing:2px;"
        )


def labeled_slider(form, label, lo, hi, val, step=1, fmt="{}", suffix="",
                   on_change=None, scale=1.0):
    """Προσθέτει στο QFormLayout έναν slider με ζωντανή ετικέτα τιμής.

    scale: ο slider δουλεύει σε ακέραια· η εμφανιζόμενη τιμή = value*scale.
    Επιστρέφει (slider, value_label).
    """
    s = QSlider(Qt.Horizontal)
    s.setRange(int(lo), int(hi))
    s.setValue(int(val))
    s.setSingleStep(step)
    vlabel = QLabel(fmt.format(val * scale) + suffix)
    vlabel.setStyleSheet(f"color:{theme.ACCENT}; font-weight:600;")

    def _upd(v):
        vlabel.setText(fmt.format(v * scale) + suffix)
        if on_change:
            on_change(v)

    s.valueChanged.connect(_upd)
    row = QHBoxLayout()
    row.addWidget(QLabel(label))
    row.addStretch()
    row.addWidget(vlabel)
    wrap = QWidget()
    wrap.setLayout(row)
    form.addRow(wrap)
    form.addRow(s)
    return s, vlabel


class ModulePage(QWidget):
    """Βασική σελίδα module: τίτλος + περιγραφή + (controls | canvas).

    Υποκλάσεις υλοποιούν build_controls(form) και build_canvas() και update_plot().
    """
    TITLE = "Module"
    SUBTITLE = ""
    DESCRIPTION = ""

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        root.addWidget(theme.heading(self.TITLE))
        if self.SUBTITLE:
            root.addWidget(theme.body(self.SUBTITLE, color=theme.TEXT, size=13))
        root.addWidget(theme.hline())

        content = QHBoxLayout()
        content.setSpacing(14)

        # ----- αριστερό panel ελέγχου (scrollable) -----
        self.control_box = QWidget()
        self.control_form = QFormLayout(self.control_box)
        self.control_form.setSpacing(8)
        self.control_form.setLabelAlignment(Qt.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.control_box)
        scroll.setMinimumWidth(330)
        scroll.setMaximumWidth(400)

        content.addWidget(scroll)

        # ----- δεξιά: καμβάς -----
        self.canvas_container = QVBoxLayout()
        content.addLayout(self.canvas_container, stretch=1)

        root.addLayout(content, stretch=1)

        # χτίσιμο από υποκλάση
        self.build_controls(self.control_form)
        self.build_canvas()
        self.update_plot()

    # --- API υποκλάσεων ---
    def build_controls(self, form):
        pass

    def build_canvas(self):
        pass

    def update_plot(self):
        pass

    # βοηθητικό για να μπει caption/θεωρία κάτω από τα controls
    def add_theory(self, html):
        self.control_form.addRow(theme.hline())
        self.control_form.addRow(theme.body(html, size=12))
