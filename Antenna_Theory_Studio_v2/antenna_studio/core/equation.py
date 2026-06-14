"""
core/equation.py — Απόδοση εξισώσεων σε LaTeX μέσω matplotlib **mathtext**
(δεν απαιτείται εγκατάσταση LaTeX). Χρησιμοποιείται από το step-by-step module.
"""

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy

from . import theme


class EquationView(FigureCanvas):
    """Καμβάς που εμφανίζει μια στοίβα από γραμμές LaTeX (mathtext)."""

    def __init__(self, figsize=(6.4, 5.2)):
        self.fig = Figure(figsize=figsize)
        self.fig.patch.set_facecolor(theme.BG_BASE)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis("off")

    def show_lines(self, lines):
        """lines: λίστα από (text, kind) όπου kind ∈ {title, eq, sub, result, note}."""
        self.ax.clear()
        self.ax.axis("off")
        self.ax.set_facecolor(theme.BG_BASE)
        styles = {
            "title":  dict(size=15, color=theme.ACCENT, weight="bold"),
            "eq":     dict(size=15, color=theme.TEXT),
            "sub":    dict(size=14, color=theme.ACCENT4),
            "result": dict(size=16, color=theme.ACCENT2, weight="bold"),
            "note":   dict(size=11, color=theme.TEXT_DIM, style="italic"),
        }
        y = 0.95
        for text, kind in lines:
            st = styles.get(kind, styles["eq"])
            dy = 0.16 if kind in ("eq", "sub", "result") else 0.10
            self.ax.text(0.04, y, text, transform=self.ax.transAxes,
                         va="top", ha="left", **st)
            y -= dy
        self.fig.canvas.draw_idle()
